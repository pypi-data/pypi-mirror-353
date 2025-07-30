"""Utility class for handling prompt template operations."""

import asyncio
import json
import logging
import os
from collections import defaultdict
from typing import List, Optional

from pydantic_ai import Agent as PydanticAgent

from agent_sdk.config import Config
from agent_sdk.core.deploy_tools.generate_metadata import MetadataGenerator
from agent_sdk.exceptions import AgentforceApiError, ValidationError
from agent_sdk.models.prompt_template import PromptInput, PromptTemplate
from agent_sdk.utils.prompt_templates.prompt_template_schema import PromptTemplateSchema

# Configure logging
logger = logging.getLogger(__name__)


class PromptTemplateUtils:
    """Utility class for handling prompt template operations."""

    def __init__(self, sf):
        """Initialize PromptTemplateUtils.

        Args:
            sf: Salesforce instance for API operations
        """
        self.sf = sf
        self.API_VERSION = Config.API_VERSION

    def generate_prompt_template(
        self,
        name: str,
        description: str,
        object_names: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        model: Optional[str] = None,
    ) -> PromptTemplate:
        """Generate a prompt template using LLM based on description and Salesforce objects.

        Args:
            name (str): Name of the prompt template
            description (str): Description of what the prompt template should do
            object_names (List[str], optional): List of Salesforce object names to consider for field mapping
            output_dir (str, optional): Directory to save the generated template.
                If not provided, template won't be saved.
            model (str, optional): The model to tune the prompt for (e.g., "gpt-4", "gpt-4o", "llama-2").
                Affects prompt style.

        Returns:
            PromptTemplate: Generated prompt template with field mappings

        Raises:
            ValidationError: If required information is missing
            AgentforceApiError: If API calls fail
        """
        logger.info(
            f"Generating prompt template '{name}' for description: {description}"
        )

        if not name or not description:
            raise ValidationError("Both name and description are required")

        try:
            # First, use LLM to analyze the description and suggest fields and template structure
            # Adjust the analysis prompt based on the model
            model_specific_instructions = ""
            if model:
                if model == "gpt-4o":
                    model_specific_instructions = """
Additional requirements for GPT-4o Optimized:
1. Keep prompts concise and focused
2. Use structured field references with clear type hints
3. Include specific context boundaries
4. Optimize for one-shot responses
5. Use explicit instruction markers"""
                elif model == "llama-2":
                    model_specific_instructions = """
Additional requirements for Llama-2:
1. Use step-by-step instruction format
2. Include more explicit examples
3. Use simpler language constructs
4. Add more context and explanations
5. Use numbered lists for instructions"""
                elif model.startswith("gpt-"):
                    model_specific_instructions = """
Additional requirements for GPT models:
1. Use clear separation between context and instructions
2. Include specific format requirements
3. Use explicit system-style instructions
4. Add validation rules where needed"""

            # If no specific objects provided, try to detect relevant ones from description
            if not object_names:
                try:
                    # Get global describe to list all available objects
                    global_describe = self.sf.describe()
                    available_objects = {
                        obj["name"]: {
                            "label": obj["label"],
                            "keyPrefix": obj.get("keyPrefix", ""),
                            "fields": [],  # Will be populated on demand
                        }
                        for obj in global_describe["sobjects"]
                        if obj["queryable"]
                        and obj["createable"]  # Only include accessible objects
                    }

                    # Look for object name mentions in the description
                    desc_lower = description.lower()
                    detected_objects = []

                    for obj_name, obj_info in available_objects.items():
                        # Check if object name or label is mentioned
                        if (
                            obj_name.lower() in desc_lower
                            or obj_info["label"].lower() in desc_lower
                        ):
                            detected_objects.append(obj_name)

                    if detected_objects:
                        object_names = detected_objects
                        logger.info(
                            f"Detected Salesforce objects from description: {', '.join(detected_objects)}"
                        )

                except Exception as e:
                    logger.warning(f"Failed to get global describe: {e!s}")

            # Get Salesforce metadata for detected objects
            sf_field_mappings = {}
            if object_names:
                for obj_name in object_names:
                    try:
                        # Get the SFType object and call describe() on it
                        sf_object = getattr(self.sf, obj_name)
                        obj_desc = sf_object.describe()
                        sf_field_mappings[obj_name] = {
                            field["name"].lower(): {
                                "type": field["type"],
                                "label": field["label"],
                                "description": field.get("inlineHelpText", ""),
                                "nillable": field.get("nillable", True),
                                "picklistValues": field.get("picklistValues", []),
                                "referenceTo": field.get("referenceTo", []),
                                "relationshipName": field.get("relationshipName", ""),
                            }
                            for field in obj_desc["fields"]
                        }
                    except Exception as e:
                        logger.warning(f"Failed to describe object {obj_name}: {e!s}")

            # Update the analysis prompt to include Salesforce metadata
            metadata_context = ""
            if sf_field_mappings:
                metadata_context = "\nAvailable Salesforce Objects and Fields:\n"
                for obj_name, fields in sf_field_mappings.items():
                    metadata_context += f"\n{obj_name}:\n"
                    for field_name, field_info in fields.items():
                        metadata_context += (
                            f"- {field_name} ({field_info['type']}): "
                            f"{field_info['description'] or field_info['label']}\n"
                        )
                        if field_info["referenceTo"]:
                            metadata_context += f"  References: {', '.join(field_info['referenceTo'])}\n"

            system_prompt = """You are an expert in Salesforce development and prompt engineering.
Your task is to generate a prompt template based on the given description and available Salesforce metadata.

Important Guidelines:
1. Input fields can be:
   a. Primitive types (string, number, boolean, etc.)
   b. Salesforce SObject field references
   c. Apex action outputs for related data queries
2. For Salesforce field references:
   - Use format {{!input.objectName.fieldName}}
   - Example: {{!input.case.subject}}, {{!input.account.name}}
3. For primitive types:
   - Use format {{!input.fieldName}}
   - Example: {{!input.maxResults}}, {{!input.includeHistory}}
4. For Apex action outputs:
   - If you need to query related data (e.g., recent opportunities, open cases), specify an Apex action
   - Use format {{!input.apex.ActionName}} in the template
   - The action will be generated automatically
5. Consider field types when suggesting usage:
   - Use appropriate primitive types for configuration/control fields
   - Use SObject references for direct Salesforce data fields
   - Use Apex actions for related data queries that need filtering/processing
6. Relationship fields should use dot notation:
   - Example: {{!input.case.account.name}} for Case's related Account name

Remember:
1. Use primitive types for configuration/control parameters
2. Use SObject references for direct Salesforce data fields
3. Suggest Apex actions for complex related data queries
4. Make the prompt_template natural and conversational
5. Include specific, relevant instructions"""

            user_prompt = f"""Create a prompt template based on the following description:

Description: {description}

{metadata_context}

{model_specific_instructions}"""

            # Create Pydantic AI agent for template generation
            template_generator = PydanticAgent(
                model="openai:gpt-4o",
                system_prompt=system_prompt,
                output_type=PromptTemplateSchema,
            )

            try:
                # Generate template using Pydantic AI (synchronous)
                logger.info("Calling LLM to generate prompt template")
                result = template_generator.run_sync(user_prompt)

                # Get the structured output from Pydantic AI
                llm_analysis = result.data

                logger.debug(f"Generated template schema: {llm_analysis}")

            except Exception as e:
                logger.error(f"LLM generation failed: {e!s}", exc_info=True)
                raise AgentforceApiError("Failed to generate prompt template") from e

            # Convert LLM suggested inputs to Input model instances and handle Apex actions
            input_fields = []
            apex_actions = []

            # Process each input field from LLM analysis
            for field in llm_analysis.inputs:
                field_data = {
                    "name": field.name,
                    "data_type": field.data_type,
                    "description": field.description,
                    "is_required": field.required,
                }

                if field.requires_apex_query and field.apex_action:
                    # Store Apex action info for later generation
                    apex_actions.append(
                        {
                            "name": field.apex_action.name,
                            "description": field.apex_action.description,
                            "parent_object": field.apex_action.parent_object,
                            "query_type": field.apex_action.query_type,
                        }
                    )

                    # Add Apex reference field
                    field_data.update(
                        {
                            "data_type": "apex",
                            "salesforce_field": field.apex_action.name,
                            "salesforce_object": "apex",
                        }
                    )
                elif field.is_sobject_field and field.salesforce_mapping:
                    # Add Salesforce field mapping
                    field_data.update(
                        {
                            "salesforce_field": field.salesforce_mapping.field,
                            "salesforce_object": field.salesforce_mapping.object,
                        }
                    )

                input_fields.append(PromptInput(**field_data))

            # Group and process fields for template
            grouped_fields = defaultdict(list)
            for field in input_fields:
                group = (
                    "primitive"
                    if not field.salesforce_object
                    else field.salesforce_object
                )
                grouped_fields[group].append(field)

            # Process template text and create final fields list
            template_text = llm_analysis.prompt_template
            final_fields = []

            for object_name, fields in grouped_fields.items():
                if object_name == "primitive":
                    final_fields.extend(fields)
                else:
                    # Add object reference field for non-primitive types
                    if object_name != "apex":
                        field = fields[0]
                        final_fields.append(
                            PromptInput(
                                name=field.salesforce_object.lower(),
                                data_type=field.salesforce_object,
                                description=field.description,
                                is_required=field.is_required,
                            )
                        )
                    # Update template placeholders
                    for field in fields:
                        if object_name != "primitive":
                            template_text = template_text.replace(
                                f"{{!input.{field.name}}}",
                                f"{{!$Input:{field.salesforce_object.lower()}.{field.salesforce_field}}}",
                            )
                        else:
                            template_text = template_text.replace(
                                f"{{!input.{field.name}}}", f"{{!$Input:{field.name}}}"
                            )

            # Generate Apex classes if needed
            if output_dir and apex_actions:
                apex_dir = os.path.join(output_dir or os.getcwd(), "apex")
                os.makedirs(apex_dir, exist_ok=True)

                # Define async helper function
                async def generate_apex_action_async(action):
                    try:
                        apex_code = await self._generate_apex_action_async(
                            class_name=action["name"],
                            parent_object=action["parent_object"],
                            query_type=action["query_type"],
                            description=action["description"],
                            input_fields=final_fields,
                        )

                        with open(
                            os.path.join(apex_dir, f"{action['name']}.cls"), "w"
                        ) as f:
                            f.write(apex_code)

                        logger.info(f"Generated Apex action: {action['name']}")
                        return {
                            "success": True,
                            "name": action["name"],
                            "description": action["description"],
                            "apex_code": apex_code,
                        }
                    except Exception as e:
                        logger.error(
                            f"Failed to generate Apex action {action['name']}: {e!s}"
                        )
                        return {
                            "success": False,
                            "name": action["name"],
                            "error": str(e),
                        }

                # Generate data query Apex classes in parallel
                async def generate_all_actions():
                    tasks = [
                        generate_apex_action_async(action) for action in apex_actions
                    ]
                    return await asyncio.gather(*tasks)

                # Run the async code in an event loop
                results = asyncio.run(generate_all_actions())

                # Process results and update template text
                for result in results:
                    if result["success"]:
                        template_text = (
                            template_text
                            + "\n\n"
                            + result["description"]
                            + ":\n"
                            + f"{{!$Apex:.{result['name']}}}\n"
                        )

                # Generate prompt template Apex class
                template_class_name = f"{name.replace(' ', '')}Template"

                # Define a helper function for template generation
                async def generate_template_class():
                    try:
                        prompt_apex_code = await self._generate_apex_action_async(
                            class_name=template_class_name,
                            parent_object="",  # Not needed for prompt template
                            query_type="prompt",
                            description=description,
                            input_fields=final_fields,
                        )

                        with open(
                            os.path.join(apex_dir, f"{template_class_name}.cls"), "w"
                        ) as f:
                            f.write(prompt_apex_code)

                        logger.info(
                            f"Generated prompt template Apex class: {template_class_name}"
                        )
                        return True
                    except Exception as e:
                        logger.error(f"Failed to generate template Apex class: {e!s}")
                        return False

                # Run the template generation
                asyncio.run(generate_template_class())

            # Create final template
            template = PromptTemplate(
                name=name,
                description=description,
                input_fields=final_fields,
                output_fields=[],
                template_text=template_text,
            )

            # Save the template if output directory is provided
            if output_dir:
                self.save_prompt_template(template, output_dir)

            logger.info(f"Successfully generated prompt template: {name}")
            return template

        except Exception as e:
            logger.error(
                f"Failed to generate prompt template '{name}': {e!s}", exc_info=True
            )
            raise AgentforceApiError("Failed to generate prompt template") from e

    def _generate_apex_action(
        self,
        class_name: str,
        parent_object: str,
        query_type: str,
        description: str,
        input_fields: Optional[List[PromptInput]] = None,
    ) -> str:
        """Generate an Apex invocable action for querying related data or prompt templates.

        Args:
            class_name (str): Name of the Apex class
            parent_object (str): Parent Salesforce object (e.g., Account)
            query_type (str): Type of query (e.g., RecentOpportunities) or 'prompt' for templates
            description (str): Description of what the action does
            input_fields (List[PromptInput], optional): List of input fields for prompt templates

        Returns:
            str: Generated Apex code
        """
        logger.info(
            f"Generating Apex action class: {class_name} for {parent_object} with query type {query_type}"
        )

        try:
            # Use the synchronous wrapper to generate Apex code
            input_fields_str = ""
            if query_type == "prompt" and input_fields:
                # Format input fields as JSON for the prompt
                input_fields_json = []
                for field in input_fields:
                    input_fields_json.append(
                        {
                            "name": field.name,
                            "object": field.salesforce_object,
                            "field": field.salesforce_field,
                            "required": field.is_required,
                        }
                    )
                input_fields_str = json.dumps(input_fields_json, indent=2)

            # Prevents openai keys being required at import time
            from agent_sdk.utils.prompt_templates.apex_generator_graph import (
                generate_apex_code_sync,
            )

            apex_code = generate_apex_code_sync(
                class_name=class_name,
                parent_object=parent_object,
                query_type=query_type,
                description=description,
                input_fields=input_fields_str,
                max_iterations=3,
            )

            return apex_code

        except Exception as e:
            logger.error(
                f"Failed to generate Apex action {class_name}: {e!s}", exc_info=True
            )
            raise AgentforceApiError("Failed to generate Apex action") from e

    async def _generate_apex_action_async(
        self,
        class_name: str,
        parent_object: str,
        query_type: str,
        description: str,
        input_fields: Optional[List[PromptInput]] = None,
    ) -> str:
        """Async version of _generate_apex_action for better parallel performance.

        Args:
            class_name (str): Name of the Apex class
            parent_object (str): Parent Salesforce object (e.g., Account)
            query_type (str): Type of query (e.g., RecentOpportunities) or 'prompt' for templates
            description (str): Description of what the action does
            input_fields (List[PromptInput], optional): List of input fields for prompt templates

        Returns:
            str: Generated Apex code
        """
        from agent_sdk.utils.prompt_templates.apex_generator_graph import (
            generate_apex_code,
        )

        logger.info(f"Generating Apex action class asynchronously: {class_name}")

        try:
            # Format input fields as JSON for the prompt
            input_fields_str = ""
            if query_type == "prompt" and input_fields:
                input_fields_json = []
                for field in input_fields:
                    input_fields_json.append(
                        {
                            "name": field.name,
                            "object": field.salesforce_object,
                            "field": field.salesforce_field,
                            "required": field.is_required,
                        }
                    )
                input_fields_str = json.dumps(input_fields_json, indent=2)

            # Generate Apex code using the async version
            apex_code = await generate_apex_code(
                class_name=class_name,
                parent_object=parent_object,
                query_type=query_type,
                description=description,
                input_fields=input_fields_str,
                max_iterations=3,
            )

            return apex_code

        except Exception as e:
            logger.error(
                f"Failed to asynchronously generate Apex action {class_name}: {e!s}",
                exc_info=True,
            )
            raise AgentforceApiError("Failed to generate Apex action") from e

    def save_prompt_template(self, template: PromptTemplate, output_dir: str) -> str:
        """Save a prompt template to the specified output directory.

        Args:
            template (PromptTemplate): The prompt template to save
            output_dir (str): Directory to save the template

        Returns:
            str: Path to the saved template file

        Raises:
            ValidationError: If required information is missing
            AgentforceApiError: If saving fails
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Create a sanitized filename from the template name
            template_name = MetadataGenerator._sanitize_name(template.name).lower()
            template_file = os.path.join(output_dir, f"{template_name}.json")

            # Convert template to dictionary format
            template_data = template.to_dict()

            # Save the template
            with open(template_file, "w") as f:
                json.dump(template_data, f, indent=2)

            logger.info(f"Successfully saved prompt template to: {template_file}")
            return template_file

        except Exception as e:
            logger.error(f"Failed to save prompt template: {e!s}")
            raise AgentforceApiError("Failed to save prompt template") from e

    def load_template(self, template_path: str) -> PromptTemplate:
        """Load a prompt template from a JSON file.

        Args:
            template_path (str): Path to the template JSON file

        Returns:
            PromptTemplate: Loaded prompt template

        Raises:
            ValidationError: If the file doesn't exist or has invalid format
            AgentforceApiError: If loading fails
        """
        try:
            if not os.path.exists(template_path):
                raise ValidationError(f"Template file not found: {template_path}")

            with open(template_path, "r") as f:
                template_data = json.load(f)

            return PromptTemplate.from_dict(template_data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse template file: {e!s}")
            raise ValidationError(f"Invalid template format in {template_path}") from e
        except Exception as e:
            logger.error(f"Failed to load template: {e!s}")
            raise AgentforceApiError("Failed to load template") from e

    def tune_prompt_template(
        self,
        template_path: str,
        description: str,
        model: str,
        output_dir: Optional[str] = None,
    ) -> PromptTemplate:
        """Tune an existing prompt template for a specific model and enhance it based on description.

        Args:
            template_path (str): Path to the existing template JSON file
            description (str): Additional description or context for tuning
            model (str): The model to tune the template for (e.g., "gpt-4", "gpt-4o", "llama-2")
            output_dir (str, optional): Directory to save the tuned template. If not provided, won't save.

        Returns:
            PromptTemplate: Tuned prompt template with enhanced fields and instructions

        Raises:
            ValidationError: If required information is missing
            AgentforceApiError: If API calls fail
        """
        logger.info(f"Tuning prompt template from {template_path} for model: {model}")

        try:
            # Load the existing template
            with open(template_path, "r") as f:
                existing_template = json.load(f)

            # Convert to PromptTemplate instance
            current_template = PromptTemplate.from_dict(existing_template)

            # Create enhanced description combining original and new context
            enhanced_description = f"""Original Template Description: {current_template.description}
Additional Context/Requirements: {description}

Current Template Structure:
{current_template.template_text}"""

            # Generate enhanced template using the existing method
            enhanced_template = self.generate_prompt_template(
                name=f"{current_template.name}_enhanced_{model}",
                description=enhanced_description,
                object_names=[
                    field.salesforce_object
                    for field in current_template.input_fields
                    if field.salesforce_object
                ],
                output_dir=output_dir,
                model=model,
            )

            logger.info(f"Successfully enhanced template for {model}")
            return enhanced_template

        except Exception as e:
            logger.error(f"Failed to tune prompt template: {e!s}")
            raise AgentforceApiError("Failed to tune prompt template") from e
