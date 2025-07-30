"""Apex code generator using Pydantic Graph for validation and refinement."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent, format_as_xml
from pydantic_ai.messages import ModelMessage
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

# Configure logging
logger = logging.getLogger(__name__)

MODEL = "openai:gpt-4o"

# Shared example format to be used across prompts
EXAMPLE_FORMAT_PROMPT = """
public class <ClassName> {{
    @InvocableMethod
    public static List<Response> getPrompt(List<Request> requests) {{
        Request input = requests[0];
        List<Response> responses = new List<Response>();
        Response output = new Response();

        try {{
            // Create a map to hold the field values
            Map<String, Object> promptData = new Map<String, Object>();

            // Add field values to the map
            // Example: promptData.put('accountName', input.Account.Name);

            // Convert the map to a JSON string
            output.Prompt = JSON.serialize(promptData);
        }} catch(Exception e) {{
            output.Prompt = JSON.serialize(new Map<String, Object>{{
                'error' => e.getMessage(),
                'stackTrace' => e.getStackTraceString()
            }});
        }}

        responses.add(output);
        return responses;
    }}

    public class Request {{
        // Input fields here with @InvocableVariable
    }}

    public class Response {{
        @InvocableVariable(required=true)
        public String Prompt;
    }}
}}
"""

EXAMPLE_FORMAT_QUERY = """
public class <ClassName> {{
    @InvocableMethod
    public static List<Response> execute(List<Request> requests) {{
        Request input = requests[0];
        Response output = new Response();

        try {{
            // Query the data
            List<SObject> results = [/* Your SOQL query here */];

            // Convert results to a map/list structure
            List<Map<String, Object>> formattedResults = new List<Map<String, Object>>();
            for(SObject record : results) {{
                formattedResults.add(record.getPopulatedFieldsAsMap());
            }}

            // Serialize the results to JSON
            output.Prompt = JSON.serialize(formattedResults);

        }} catch(Exception e) {{
            output.Prompt = JSON.serialize(new Map<String, Object>{{
                'error' => e.getMessage(),
                'stackTrace' => e.getStackTraceString()
            }});
        }}

        return new List<Response>>{{ output }};
    }}

    public class Request {{
        @InvocableVariable(required=true)
        public Id recordId;
    }}

    public class Response {{
        @InvocableVariable(required=true)
        public String Prompt;
    }}
}}

"""

# Shared important requirements
APEX_REQUIREMENTS = """
IMPORTANT:
1. The Response class MUST be exactly as shown above, with only a single Prompt field
2. All outputs MUST be JSON serialized strings
3. Include proper error handling with JSON formatted error responses
"""


def get_example(example_format: str, class_name: str) -> str:
    """Replaces the ClassNameHere placeholder with the actual class name."""
    return example_format.replace("<ClassName>", class_name)


class ApexValidationFeedback(BaseModel):
    """Feedback on generated Apex code."""

    is_valid: bool = Field(
        description="Whether the code is valid and meets requirements"
    )
    feedback: str = Field(
        description="Detailed feedback and suggestions for improvement"
    )


@dataclass
class ApexGenerationState:
    """State for the Apex generation graph."""

    class_name: str
    parent_object: str
    query_type: str
    description: str
    input_fields: Optional[list] = None
    generated_code: str = ""
    validation_iterations: int = 0
    max_iterations: int = 3
    generation_messages: List[ModelMessage] = field(default_factory=list)
    validation_messages: List[ModelMessage] = field(default_factory=list)
    refinement_messages: List[ModelMessage] = field(default_factory=list)


# Define the agents
apex_generator_agent = Agent(
    MODEL,
    system_prompt=format_as_xml(
        """
    <role>
    You are an expert Salesforce developer specializing in Apex invocable actions.
    Your primary function is generating high-quality, well-structured Apex code.
    </role>

    <strict_requirements>
    1. The Response class MUST have ONLY a single Prompt field
    2. ALL outputs MUST be JSON serialized strings
    3. You MUST include proper error handling with JSON formatted error responses
    4. You MUST follow the exact structure provided in examples
    5. Your code MUST be properly indented and well-documented
    </strict_requirements>

    <thought_process>
    First, I'll create the class structure following the expected format.
    Then I'll craft an efficient SOQL query to retrieve the requested data.
    I'll implement proper error handling and consider governor limits.
    Finally, I'll ensure all data is properly serialized to JSON format.
    </thought_process>

    <output_format>
    You will ONLY provide complete, production-ready Apex code.
    Do not include explanations or commentary outside the code.
    If your response includes code blocks, I will extract the code from between them.
    </output_format>
    """
    ),
)

apex_validator_agent = Agent(
    MODEL,
    output_type=ApexValidationFeedback,
    system_prompt=format_as_xml(
        """
    <role>
    You are an expert Salesforce developer specializing in Apex code validation.
    Your primary function is to thoroughly analyze code for correctness and best practices.
    </role>

    <validation_approach>
    1. First examine the class structure and implementation
    2. Check for syntax errors and logical issues
    3. Verify proper error handling and JSON serialization
    4. Assess adherence to Salesforce best practices
    5. Be thorough but fair in your assessment
    </validation_approach>

    <validation_criteria>
    1. Correct class structure and naming
    2. Proper error handling
    3. Proper SOQL queries (if applicable)
    4. Proper serialization of outputs
    5. Following of Salesforce best practices
    6. Any syntax errors or bugs
    </validation_criteria>

    <output_format>
    You will provide structured feedback with:
    - A boolean indicating if the code is valid
    - Specific, actionable feedback on what needs improvement
    - Clear explanations for any issues found
    </output_format>
    """
    ),
)

apex_refiner_agent = Agent(
    MODEL,
    system_prompt=format_as_xml(
        """
    <role>
    You are an expert Salesforce developer specializing in Apex code refinement.
    Your primary function is to improve code based on validation feedback.
    </role>

    <refinement_approach>
    1. Understand validation feedback completely
    2. Make precise changes to address each issue
    3. Maintain the existing code structure where possible
    4. Ensure changes follow Salesforce best practices
    5. Verify all requirements are met before submitting
    </refinement_approach>

    <strict_requirements>
    1. The Response class MUST have ONLY a single Prompt field
    2. ALL outputs MUST be JSON serialized strings
    3. You MUST include proper error handling with JSON formatted error responses
    4. You MUST follow the exact structure provided in examples
    </strict_requirements>

    <output_format>
    You will ONLY provide the complete refined Apex implementation.
    Do not include explanations or commentary outside the code.
    If your response includes code blocks, I will extract the code from between them.
    </output_format>
    """
    ),
)


@dataclass
class GenerateApexCode(BaseNode[ApexGenerationState]):
    """Generate initial Apex code."""

    async def run(
        self, ctx: GraphRunContext[ApexGenerationState]
    ) -> "ValidateApexCode":
        logger.info(f"Generating Apex code for class: {ctx.state.class_name}")

        if ctx.state.query_type == "prompt" and ctx.state.input_fields:
            # Generate prompt template Apex class
            prompt = f"""
            <task>Generate an Apex Invocable Action class for prompt template</task>

            <specifications>
            Class Name: {ctx.state.class_name}
            Description: {ctx.state.description}
            Type: Prompt Template
            </specifications>

            <input_fields>
            {format_as_xml(ctx.state.input_fields)}
            </input_fields>

            <requirements>
            1. Create an Invocable Action that takes input fields as Request class parameters
            2. Return a Response class with ONLY a single Prompt field
            3. Include proper error handling
            4. Include appropriate comments and documentation
            5. Use JSON.serialize() for any complex data structures
            6. Must follow the exact structure provided in <example_format>
            </requirements>

            <example_format>
            {get_example(EXAMPLE_FORMAT_PROMPT, ctx.state.class_name)}
            </example_format>

            <thought_process>
            First, I'll create the class structure following the example format.
            Then I'll define the Request class with all required input fields.
            Next, I'll implement the Invocable Method to process the inputs.
            I'll ensure proper error handling throughout the code.
            Finally, I'll verify that outputs are properly serialized to JSON.
            </thought_process>
            """
        else:
            # Generate data query Apex class
            prompt = f"""
            <task>Generate an Apex Invocable Action class for data query</task>

            <specifications>
            Class Name: {ctx.state.class_name}
            Description: {ctx.state.description}
            Parent Object: {ctx.state.parent_object}
            Query Type: {ctx.state.query_type}
            </specifications>

            <requirements>
            1. Create an Invocable Action that takes a {ctx.state.parent_object} Id as input
            2. Query for {ctx.state.query_type} related to the {ctx.state.parent_object}
            3. Include proper error handling and limits checking
            4. Return a Response class with ONLY a single Prompt field containing the JSON serialized query results
            5. Follow Salesforce best practices
            6. Use JSON.serialize() for the output
            7. Must follow the exact structure provided in <example_format>
            </requirements>

            <example_format>
            {get_example(EXAMPLE_FORMAT_QUERY, ctx.state.class_name)}
            </example_format>


            """

        # Generate code
        result = await apex_generator_agent.run(
            prompt, message_history=ctx.state.generation_messages
        )

        ctx.state.generation_messages += result.all_messages()

        # Extract the Apex code from the response
        apex_code = result.data

        # Clean up the code if wrapped in Markdown code blocks
        if "```apex" in apex_code:
            apex_code = apex_code.split("```apex")[1].split("```")[0].strip()
        elif "```java" in apex_code:
            apex_code = apex_code.split("```java")[1].split("```")[0].strip()
        elif "```" in apex_code:
            apex_code = apex_code.split("```")[1].split("```")[0].strip()

        ctx.state.generated_code = apex_code
        logger.info(f"Generated initial Apex code for {ctx.state.class_name}")

        return ValidateApexCode()


@dataclass
class ValidateApexCode(BaseNode[ApexGenerationState]):
    """Validate the generated or refined Apex code."""

    async def run(
        self, ctx: GraphRunContext[ApexGenerationState]
    ) -> "RefineApexCode" | End[str]:
        logger.info(
            f"Validating Apex code (iteration {ctx.state.validation_iterations + 1})"
        )

        validation_prompt = format_as_xml(
            f"""
        <code_to_validate>
        {ctx.state.generated_code}
        </code_to_validate>

        <example_format>
        {get_example(EXAMPLE_FORMAT_PROMPT if ctx.state.query_type == 'prompt' else EXAMPLE_FORMAT_QUERY, ctx.state.class_name)}
        </example_format>

        <requirements>
        1. Class Name: {ctx.state.class_name}
        2. Description: {ctx.state.description}
        3. {"Parent Object: " + ctx.state.parent_object if ctx.state.parent_object else "Input Fields provided"}
        4. {"Query Type: " + ctx.state.query_type if ctx.state.query_type != 'prompt' else "Type: Prompt Template"}
        5. The Response class MUST have only a single Prompt field
        6. All outputs MUST be JSON serialized strings
        7. Must include proper error handling with JSON formatted error responses
        8. Must follow the exact structure provided in <example_format>
        </requirements>
        """
        )

        result = await apex_validator_agent.run(
            validation_prompt, message_history=ctx.state.validation_messages
        )

        ctx.state.validation_messages += result.all_messages()
        feedback = result.data

        # Check if validation passed or if we've reached max iterations
        if (
            ctx.state.validation_iterations >= ctx.state.max_iterations - 1
            or feedback.is_valid
        ):

            if ctx.state.validation_iterations >= ctx.state.max_iterations - 1:
                logger.info(
                    f"Reached maximum iterations ({ctx.state.max_iterations}), returning current code"
                )
            else:
                logger.info("Validation passed, returning Apex code")

            return End(ctx.state.generated_code)
        else:
            # Increment iteration counter
            ctx.state.validation_iterations += 1
            logger.info(
                f"Validation failed, proceeding to refinement with feedback: {feedback.feedback}"
            )
            return RefineApexCode(feedback=feedback.feedback)


@dataclass
class RefineApexCode(BaseNode[ApexGenerationState, None, str]):
    """Refine Apex code based on validation feedback."""

    feedback: str

    async def run(self, ctx: GraphRunContext[ApexGenerationState]) -> ValidateApexCode:
        logger.info(
            f"Refining Apex code based on feedback (iteration {ctx.state.validation_iterations})"
        )

        refinement_prompt = format_as_xml(
            f"""
        <code_to_refine>
        {ctx.state.generated_code}
        </code_to_refine>

        <validation_feedback>
        {self.feedback}
        </validation_feedback>

        <requirements>
        1. Class Name: {ctx.state.class_name}
        2. Description: {ctx.state.description}
        3. {"Parent Object: " + ctx.state.parent_object if ctx.state.parent_object else "Input Fields provided"}
        4. {"Query Type: " + ctx.state.query_type if ctx.state.query_type != 'prompt' else "Type: Prompt Template"}
        </requirements>

        <example_format>
        {get_example(EXAMPLE_FORMAT_PROMPT if ctx.state.query_type == 'prompt' else EXAMPLE_FORMAT_QUERY, ctx.state.class_name)}
        </example_format>
        """
        )

        result = await apex_refiner_agent.run(
            refinement_prompt, message_history=ctx.state.refinement_messages
        )

        ctx.state.refinement_messages += result.all_messages()

        # Extract the refined Apex code
        refined_code = result.data

        # Clean up the code if wrapped in Markdown code blocks
        if "```apex" in refined_code:
            refined_code = refined_code.split("```apex")[1].split("```")[0].strip()
        elif "```java" in refined_code:
            refined_code = refined_code.split("```java")[1].split("```")[0].strip()
        elif "```" in refined_code:
            refined_code = refined_code.split("```")[1].split("```")[0].strip()

        ctx.state.generated_code = refined_code
        logger.info("Refined Apex code, proceeding to validation")

        return ValidateApexCode()


# Define the Apex generation graph
apex_generation_graph = Graph(
    nodes=(GenerateApexCode, ValidateApexCode, RefineApexCode)
)


async def generate_apex_code(
    class_name: str,
    parent_object: str,
    query_type: str,
    description: str,
    input_fields=None,
    max_iterations: int = 3,
) -> str:
    """
    Generate Apex code with validation and refinement.

    Args:
        class_name: Name of the Apex class
        parent_object: Parent Salesforce object
        query_type: Type of query or 'prompt' for templates
        description: Description of what the action does
        input_fields: List of input fields for prompt templates
        max_iterations: Maximum number of validation-refinement iterations

    Returns:
        Generated and validated Apex code
    """
    state = ApexGenerationState(
        class_name=class_name,
        parent_object=parent_object,
        query_type=query_type,
        description=description,
        input_fields=input_fields,
        max_iterations=max_iterations,
    )

    result = await apex_generation_graph.run(GenerateApexCode(), state=state)

    return result.output


def generate_apex_code_sync(
    class_name: str,
    parent_object: str,
    query_type: str,
    description: str,
    input_fields=None,
    max_iterations: int = 3,
) -> str:
    """
    Synchronous wrapper for generating Apex code with validation and refinement.

    Args:
        class_name: Name of the Apex class
        parent_object: Parent Salesforce object
        query_type: Type of query or 'prompt' for templates
        description: Description of what the action does
        input_fields: List of input fields for prompt templates
        max_iterations: Maximum number of validation-refinement iterations

    Returns:
        Generated and validated Apex code
    """
    return asyncio.run(
        generate_apex_code(
            class_name=class_name,
            parent_object=parent_object,
            query_type=query_type,
            description=description,
            input_fields=input_fields,
            max_iterations=max_iterations,
        )
    )
