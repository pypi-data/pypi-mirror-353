"""Utility class for AgentForce SDK."""

import json
import os
from typing import Any, Dict, Union

from pydantic_ai import Agent as PydanticAgent

from agent_sdk.models import (
    Action,
    Agent,
    AttributeMapping,
    Input,
    Output,
    SystemMessage,
    Topic,
    Variable,
)


class AgentUtils:
    """Utility class for agent-related operations."""

    @staticmethod
    def _generate_action_description(action_name: str) -> str:
        """Generate a default description for an action based on its name.

        Args:
            action_name (str): The name of the action

        Returns:
            str: A generated description for the action
        """
        # Convert camelCase to space-separated words
        words = []
        current_word = ""
        for char in action_name:
            if char.isupper() and current_word:
                words.append(current_word)
                current_word = char
            else:
                current_word += char
        words.append(current_word)

        # Join words and capitalize first letter
        description = " ".join(words).lower()
        return description[0].upper() + description[1:]

    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """Load a JSON file.

        Args:
            file_path (str): Path to the JSON file

        Returns:
            dict: Loaded JSON data

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file isn't valid JSON
        """
        with open(file_path, "r") as f:
            return json.load(f)

    @staticmethod
    def save_json(file_path: str, data: Dict[str, Any], indent: int = 2) -> None:
        """Save data to a JSON file.

        Args:
            file_path (str): Path to save the file to
            data (dict): Data to save
            indent (int): Indentation level for the JSON output

        Raises:
            IOError: If the file can't be written
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=indent)

    @staticmethod
    def create_agent_from_file(file_path: str, dependent_metadata_dir: str = None) -> Agent:
        """Create an Agent instance from a JSON file.

        Args:
            file_path (str): Path to the JSON file containing agent configuration
            dependent_metadata_dir (str, optional): Path to folder containing custom metadata files

        Returns:
            Agent: Created Agent instance

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file isn't valid JSON
            KeyError: If required fields are missing from the JSON
        """
        agent_config = AgentUtils.load_json(file_path)

        # Create the agent with required fields
        agent = Agent(
            name=agent_config["name"],
            description=agent_config["description"],
            agent_type=agent_config["agent_type"],
            company_name=agent_config["company_name"],
        )

        # Set optional fields
        if "sample_utterances" in agent_config:
            agent.sample_utterances = agent_config["sample_utterances"]

        # Set system messages if present
        if "system_messages" in agent_config:
            agent.system_messages = [
                SystemMessage(**msg) for msg in agent_config["system_messages"]
            ]

        # Set variables if present
        if "variables" in agent_config:
            agent.variables = [Variable(**var) for var in agent_config["variables"]]

        # Create topics if present
        if "topics" in agent_config:
            topics = []
            for topic_data in agent_config["topics"]:
                # Create topic
                topic = Topic(
                    name=topic_data["name"],
                    description=topic_data["description"],
                    scope=topic_data["scope"],
                )

                # Set instructions if present
                if "instructions" in topic_data:
                    topic.instructions = topic_data["instructions"]

                # Create actions if present
                if "actions" in topic_data:
                    actions = []
                    for action_data in topic_data["actions"]:
                        # Convert example_output to proper Output format if present
                        output = None
                        if "example_output" in action_data:
                            example_output = action_data["example_output"]
                            if isinstance(example_output, dict):
                                # Extract status and details from the example output
                                status = example_output.get("status", "success")
                                # Remove status from details if it exists
                                details = example_output.copy()
                                details.pop("status", None)
                                output = Output(status=status, details=details)
                            else:
                                # If it's not a dict, create a simple success output
                                output = Output(
                                    status="success", details={"output": example_output}
                                )

                        # Generate description if not provided
                        description = action_data.get(
                            "description",
                            AgentUtils._generate_action_description(
                                action_data["name"]
                            ),
                        )

                        action = Action(
                            name=action_data["name"],
                            description=description,
                            inputs=[
                                Input(**input_data)
                                for input_data in action_data["inputs"]
                            ],
                            outputs=[
                                Output(**output_data)
                                for output_data in action_data.get("outputs", [])
                            ],
                            example_output=output,
                        )
                        
                        # Handle attribute mappings if present
                        if "attribute_mappings" in action_data:
                            for mapping_data in action_data["attribute_mappings"]:
                                # Find the variable by name from agent variables
                                variable_name = mapping_data.get("variable_name", "")
                                variable_obj = None
                                
                                # Search for the variable in agent variables
                                for var in agent.variables:
                                    if var.name == variable_name:
                                        variable_obj = var
                                        break
                                
                                if variable_obj:
                                    # Create AttributeMapping object
                                    attr_mapping = AttributeMapping(
                                        action_parameter=mapping_data.get("action_parameter", ""),
                                        variable=variable_obj,
                                        direction=mapping_data.get("direction", "input")
                                    )
                                    action.attribute_mappings.append(attr_mapping)
                            
                        actions.append(action)
                    topic.actions = actions

                topics.append(topic)
            agent.topics = topics

        return agent

    @staticmethod
    def create_agent_directory_structure(
        base_dir: str, agent_data: Union[Dict[str, Any], str]
    ) -> None:
        """Create a directory structure for an agent.

        This creates the following structure:
        - base_dir/
          - agent.json: Main agent configuration (without topics)
          - topics/
            - <topic_name>.json: Topic configuration (without actions)
            - <topic_name>/
              - actions/
                - <action_name>.json: Action configuration

        Args:
            base_dir (str): Base directory to create the structure in
            agent_data (Union[Dict[str, Any], str]): Either a dictionary with agent data or a path to a JSON file
        """
        # Handle string input (file path)
        if isinstance(agent_data, str):
            try:
                # If it's a path to a JSON file, load it
                agent_data = AgentUtils.load_json(agent_data)
            except Exception as e:
                raise ValueError(
                    f"Failed to load agent data from {agent_data}: {str(e)}"
                )

        # Create directories
        os.makedirs(base_dir, exist_ok=True)
        topics_dir = os.path.join(base_dir, "topics")
        os.makedirs(topics_dir, exist_ok=True)

        # Copy agent data and remove topics
        agent_copy = agent_data.copy()
        topics = agent_copy.pop("topics", [])

        # Save agent.json
        agent_filename = (
            os.path.basename(base_dir) + ".json"
            if os.path.basename(base_dir)
            else "agent.json"
        )
        AgentUtils.save_json(os.path.join(base_dir, agent_filename), agent_copy)

        # Process topics
        for topic in topics:
            # Check if topic is a dictionary or an object
            if isinstance(topic, dict):
                topic_name = topic["name"].lower().replace(" ", "_")
                topic_copy = topic.copy()
                actions = topic_copy.pop("actions", [])
            else:
                topic_name = topic.name.lower().replace(" ", "_")
                topic_copy = topic.__dict__.copy()
                actions = topic_copy.pop("actions", [])

            # Save topic json
            AgentUtils.save_json(
                os.path.join(topics_dir, f"{topic_name}.json"), topic_copy
            )

            # Process actions
            if actions:
                # Create actions directory
                actions_dir = os.path.join(topics_dir, topic_name, "actions")
                os.makedirs(actions_dir, exist_ok=True)

                for action in actions:
                    # Check if action is a dictionary or an object
                    if isinstance(action, dict):
                        action_name = action["name"].lower().replace(" ", "_")
                        action_data = action
                    else:
                        action_name = action.name.lower().replace(" ", "_")
                        action_data = action.__dict__

                    AgentUtils.save_json(
                        os.path.join(actions_dir, f"{action_name}.json"), action_data
                    )

    @staticmethod
    def create_agent_from_directory_structure(base_dir: str, agent_name: str, dependent_metadata_dir: str = None) -> Agent:
        """Load an agent from a directory structure.

        This expects the following structure:
        - base_dir/
          - agent.json: Main agent configuration
          - topics/
            - <topic_name>.json: Topic configuration
            - <topic_name>/
              - actions/
                - <action_name>.json: Action configuration

        Args:
            base_dir (str): Base directory containing the agent structure
            agent_name (str): Name of the agent
            dependent_metadata_dir (str, optional): Path to folder containing custom metadata files

        Returns:
            Agent: Created Agent instance
        """
        # Ensure agent_name is lowercase with spaces replaced by underscores
        agent_name = agent_name.lower().replace(" ", "_")

        # Load agent.json
        print("agent_name: ", agent_name)
        agent_file = os.path.join(base_dir, f"{agent_name}.json")
        if not os.path.exists(agent_file):
            raise FileNotFoundError(f"Agent configuration file not found: {agent_file}")
        agent_data = AgentUtils.load_json(agent_file)

        # Ensure required fields are present
        if "domain" not in agent_data:
            # Add a default domain based on company name if missing
            company_name = agent_data.get("company_name", "unknown")
            agent_data["domain"] = (
                f"https://{company_name.lower().replace(' ', '')}.com"
            )

        # Initialize topics array if not present
        if "topics" not in agent_data:
            agent_data["topics"] = []

        # Load topics
        topics_dir = os.path.join(base_dir, "topics")
        if os.path.exists(topics_dir):
            topic_files = [f for f in os.listdir(topics_dir) if f.endswith(".json")]
            for topic_file in topic_files:
                topic_path = os.path.join(topics_dir, topic_file)
                if os.path.exists(topic_path):
                    topic_data = AgentUtils.load_json(topic_path)
                    # Initialize actions array if not present
                    if "actions" not in topic_data:
                        topic_data["actions"] = []

                    # Load actions
                    topic_name = os.path.splitext(topic_file)[0]
                    actions_dir = os.path.join(topics_dir, topic_name, "actions")
                    if os.path.exists(actions_dir):
                        action_files = [
                            f for f in os.listdir(actions_dir) if f.endswith(".json")
                        ]
                        for action_file in action_files:
                            action_path = os.path.join(actions_dir, action_file)
                            if os.path.exists(action_path):
                                action_data = AgentUtils.load_json(action_path)
                                topic_data["actions"].append(action_data)
                    # Add topic to agent
                    agent_data["topics"].append(topic_data)
        # Create agent from the collected data
        return AgentUtils.create_agent_from_dict(agent_data, dependent_metadata_dir=dependent_metadata_dir)

    @staticmethod
    def create_agent_from_dict(agent_data: Dict[str, Any], dependent_metadata_dir: str = None) -> Agent:
        """Create an Agent instance from a dictionary.

        Args:
            agent_data (Dict[str, Any]): Dictionary containing agent configuration
            dependent_metadata_dir (str, optional): Path to folder containing custom metadata files

        Returns:
            Agent: Created Agent instance
        """
        # Ensure domain field exists
        if "domain" not in agent_data:
            company_name = agent_data.get("company_name", "unknown")
            agent_data["domain"] = (
                f"https://{company_name.lower().replace(' ', '')}.com"
            )

        # Create the agent with required fields
        agent = Agent(
            name=agent_data["name"],
            description=agent_data["description"],
            agent_type=agent_data["agent_type"],
            company_name=agent_data["company_name"],
            domain=agent_data["domain"],
        )

        # Set optional fields
        if "sample_utterances" in agent_data:
            agent.sample_utterances = agent_data["sample_utterances"]

        if "agent_template_type" in agent_data:
            agent.agent_template_type = agent_data["agent_template_type"]

        # Set system messages if present
        if "system_messages" in agent_data:
            agent.system_messages = [
                SystemMessage(**msg) for msg in agent_data["system_messages"]
            ]

        # Set variables if present
        if "variables" in agent_data:
            agent.variables = [Variable(**var) for var in agent_data["variables"]]

        # Create topics if present
        if "topics" in agent_data:
            topics = []
            for topic_data in agent_data["topics"]:
                # Create topic
                topic = Topic(
                    name=topic_data["name"],
                    description=topic_data["description"],
                    scope=topic_data["scope"],
                )

                # Set instructions if present
                if "instructions" in topic_data:
                    topic.instructions = topic_data["instructions"]

                # Create actions if present
                if "actions" in topic_data:
                    actions = []
                    for action_data in topic_data["actions"]:
                        # Convert example_output to proper Output format if present
                        output = None
                        if "example_output" in action_data:
                            example_output = action_data["example_output"]
                            if isinstance(example_output, dict):
                                # Extract status and details from the example output
                                status = example_output.get("status", "success")
                                # Remove status from details if it exists
                                details = example_output.copy()
                                details.pop("status", None)
                                output = Output(status=status, details=details)
                            else:
                                # If it's not a dict, create a simple success output
                                output = Output(
                                    status="success", details={"output": example_output}
                                )

                        # Generate description if not provided
                        description = action_data.get(
                            "description",
                            AgentUtils._generate_action_description(
                                action_data["name"]
                            ),
                        )

                        action = Action(
                            name=action_data["name"],
                            description=description,
                            inputs=[
                                Input(**input_data)
                                for input_data in action_data["inputs"]
                            ],
                            outputs=[
                                Output(**output_data)
                                for output_data in action_data.get("outputs", [])
                            ],
                            example_output=output,
                        )
                        
                        # Handle attribute mappings if present
                        if "attribute_mappings" in action_data:
                            for mapping_data in action_data["attribute_mappings"]:
                                # Find the variable by name from agent variables
                                variable_name = mapping_data.get("variable_name", "")
                                variable_obj = None
                                
                                # Search for the variable in agent variables
                                for var in agent.variables:
                                    if var.name == variable_name:
                                        variable_obj = var
                                        break
                                
                                if variable_obj:
                                    # Create AttributeMapping object
                                    attr_mapping = AttributeMapping(
                                        action_parameter=mapping_data.get("action_parameter", ""),
                                        variable=variable_obj,
                                        direction=mapping_data.get("direction", "input")
                                    )
                                    action.attribute_mappings.append(attr_mapping)
                            
                        actions.append(action)
                    topic.actions = actions

                topics.append(topic)
            agent.topics = topics

        return agent

    # Alias for clarity
    @staticmethod
    def create_agent_from_json_file(file_path: str, dependent_metadata_dir: str = None) -> Agent:
        """Alias for create_agent_from_file. Creates an Agent instance from a JSON file.

        Args:
            file_path (str): Path to the JSON file containing agent configuration
            dependent_metadata_dir (str, optional): Path to folder containing custom metadata files

        Returns:
            Agent: Created Agent instance
        """
        return AgentUtils.create_agent_from_file(file_path, dependent_metadata_dir=dependent_metadata_dir)

    @staticmethod
    def export_agent_to_modular_files(
        agent_data: Dict[str, Any], export_path: str
    ) -> None:
        """Export an agent configuration to modular files.

        This creates the following structure:
        - export_path/
          - agents/
            - <agent_name>.json: Agent configuration (with topic references)
          - topics/
            - <topic_name>.json: Topic configuration (with action references)
          - actions/
            - <action_name>.json: Action configuration
        """
        # Create directories
        agents_dir = os.path.join(export_path, "agents")
        topics_dir = os.path.join(export_path, "topics")
        actions_dir = os.path.join(export_path, "actions")

        os.makedirs(agents_dir, exist_ok=True)
        os.makedirs(topics_dir, exist_ok=True)
        os.makedirs(actions_dir, exist_ok=True)

        # Create a copy of the agent data
        agent_copy = agent_data.copy()

        # Create a list of topic references and copy topics
        agent_copy["topics"] = []
        topics = agent_copy.pop("topics", [])

        # Process each topic
        for topic in topics:
            topic_name = topic.name.lower().replace(" ", "_")
            agent_copy["topics"].append(topic_name)

            # Create a copy of the topic data
            topic_copy = topic.__dict__.copy()

            # Create a list of action references and copy actions
            topic_copy["actions"] = []
            actions = topic_copy.pop("actions", [])

            # Process each action
            for action in actions:
                action_name = action.name.lower().replace(" ", "_")
                topic_copy["actions"].append(action_name)

                # Add topic reference to the action
                action_copy = action.__dict__.copy()
                action_copy["topic"] = topic_name

                # Save action
                AgentUtils.save_json(
                    os.path.join(actions_dir, f"{action_name}.json"), action_copy
                )

            # Save topic
            AgentUtils.save_json(
                os.path.join(topics_dir, f"{topic_name}.json"), topic_copy
            )

        # Save agent
        agent_name = agent_copy.get("name", "agent").lower().replace(" ", "_")
        AgentUtils.save_json(os.path.join(agents_dir, f"{agent_name}.json"), agent_copy)

    @staticmethod
    def create_agent_from_modular_files(base_dir: str, agent_name: str, dependent_metadata_dir: str = None) -> Agent:
        """Create an agent from modular JSON files.
        
        Args:
            base_dir (str): Base directory containing the modular agent files
            agent_name (str): Name of the agent
            dependent_metadata_dir (str, optional): Path to folder containing custom metadata files
            
        Returns:
            Agent: Created Agent instance
        """
        # Load agent configuration
        agent_config = AgentUtils.load_json(
            os.path.join(base_dir, "agents", f"{agent_name}.json")
        )

        # Create the agent
        agent = Agent(
            name=agent_config["name"],
            description=agent_config["description"],
            agent_type=agent_config["agent_type"],
            company_name=agent_config["company_name"],
        )

        # Set sample utterances if present
        if "sample_utterances" in agent_config:
            agent.sample_utterances = agent_config["sample_utterances"]

        # Set system messages if present
        if "system_messages" in agent_config:
            agent.system_messages = [
                SystemMessage(**msg) for msg in agent_config["system_messages"]
            ]

        # Set variables if present
        if "variables" in agent_config:
            agent.variables = [Variable(**var) for var in agent_config["variables"]]

        # Load and create topics
        topics = []
        for topic_name in agent_config.get("topics", []):
            topic_config = AgentUtils.load_json(
                os.path.join(base_dir, "topics", f"{topic_name}.json")
            )

            # Create topic
            topic = Topic(
                name=topic_config["name"],
                description=topic_config["description"],
                scope=topic_config["scope"],
            )

            # Set instructions
            topic.instructions = topic_config["instructions"]

            # Load and set actions
            actions = []
            for action_name in topic_config["actions"]:
                action_config = AgentUtils.load_json(
                    os.path.join(base_dir, "actions", f"{action_name}.json")
                )

                # Get description or generate one if not present
                description = action_config.get(
                    "description",
                    AgentUtils._generate_action_description(action_config["name"]),
                )

                # Handle example_output to properly create Output object
                example_output = action_config["example_output"]
                if isinstance(example_output, dict):
                    # Extract status and details from the example output
                    status = example_output.get("status", "success")
                    # Remove status from details if it exists
                    details = example_output.copy()
                    details.pop("status", None)
                    output = Output(status=status, details=details)
                else:
                    # If it's not a dict, create a simple success output
                    output = Output(
                        status="success", details={"output": example_output}
                    )

                # Create action
                action = Action(
                    name=action_config["name"],
                    description=description,
                    inputs=[
                        Input(**input_data) for input_data in action_config["inputs"]
                    ],
                    outputs=[
                        Output(**output_data)
                        for output_data in action_config.get("outputs", [])
                    ],
                    example_output=output,
                )
                
                # Handle attribute mappings if present
                if "attribute_mappings" in action_config:
                    for mapping_data in action_config["attribute_mappings"]:
                        # Find the variable by name from agent variables
                        variable_name = mapping_data.get("variable_name", "")
                        variable_obj = None
                        
                        # Search for the variable in agent variables
                        for var in agent.variables:
                            if var.name == variable_name:
                                variable_obj = var
                                break
                        
                        if variable_obj:
                            # Create AttributeMapping object
                            attr_mapping = AttributeMapping(
                                action_parameter=mapping_data.get("action_parameter", ""),
                                variable=variable_obj,
                                direction=mapping_data.get("direction", "input")
                            )
                            action.attribute_mappings.append(attr_mapping)
                    
                actions.append(action)

            topic.actions = actions
            topics.append(topic)

        # Set topics for the agent
        agent.topics = topics
        return agent

    @staticmethod
    def generate_agent_info(
        description: str,
        company_name: str,
        agent_name: str,
        output_dir: str,
        model: str = "openai:gpt-4o",
    ) -> None:
        """Generate agent information in modular format using OpenAI.

        Args:
            description (str): Description of what the agent should do
            company_name (str): Name of the company
            agent_name (str): Name of the agent
            output_dir (str): Directory to save the generated files
            model (str): OpenAI model to use

        Returns:
            None
        """

        # Ensure agent_name is lowercase with spaces replaced by underscores
        agent_name = agent_name.lower().replace(" ", "_")

        # System message to guide the LLM
        system_message = """

         Your job is to create a description of an AI Agent, generating sample utterances, and convert a list of topics into a specific JSON format. The description of the AI Agent and the sample utterances should be combined into the JSON object. The description and sample utterances should be grounded in the context of the conversation provided.
        Always ask for the company name first and what the name of the agent should be if we don't have it already.

        # Rules:
        - When converting the Topics, description, scope, instructions and actions to JSON, DO NOT MODIFY any of the properties or language.
        - Never use or include emojis
        - Use the requirements gathered from the conversation to generate the agent metadata

        # Guidelines
        Follow these instructions carefully to complete the task:

        1. First, review the context of the conversation if provided, we provided the requirements for the agent. Come up with a name for the agent.

        2. Now, examine the list of topics to be converted:
        3. Convert each topic into the required JSON format

        4. For each topic:
        a. Use the topic name as provided in the list for the "name" field.  The topic name must only use ASCII characters and _, if there are any other characters (accents, emojis, etc...), please convert them to plain ASCII or a _ if its a space.
        b. Use the description provided in the description field. Do not change the description.
        c. Use the scope provided in the scope field. Do not change the scope.
        d. Include all of the instructions provided in the instructions list. Do not change any of the instructions
        e. Generate a list of actions for the "actions" field, following the format described in step 5. Do not change any of the action properties.
        f. Ensure you do not change the fields from the Topics
        g. Remove all '/' from the actions.
        h. Remove any actions that do Knowledge Lookups or search knowledge action. This includes but is not limited to: Knowledge_Lookup, Search_Knowledge... etc. If an instruction includes the "Knowledge_Lookup" action, modify the instruction to something like "search the knowledge base".

        5. For each action, generate an example_output as a JSON object that demonstrates its full capabilities. Rules for the example output:
        a. Provide a detailed and realistic return value
        b. Include any relevant metadata or additional information that the function might reasonably return.

        6. Generate only 1 or 2 topics if possible.

        7. Given the Topics and the Context of the conversation, generate a 1-2 description of the AI Agent and what it does. The description should start with: "You are an AI Agent whose job is to help <COMPANY> customers...."

        8. Given the Topics, Instructions, and actions, generate 4-5 sample utterances a user might use to engage with the AI Agent. These sample utterances should tie directly back to an instruction or an action. When including IDs in the sample utterances, make the IDs realistic. Do not include any utterances about escalating or speaking to a human.

        9. Ensure that all JSON is properly formatted and valid. Always return only JSON.

        ## Rules for Instructions:
        - Each instruction should be a single topic-specific guideline, usually phrased as but not limited to "If x, then y…", "As a first step,…", "Once the customer does...", "When a customer...".
        - Instructions should be non-deterministic and should not include sensitive or deterministic business rules.
        - Instructions should also provide as much context as possible, which is derived from the transcript, so that the AI Agent can have a better understanding of the use case.
        - When writing instructions, ensure that they do not conflict with each other within a topic.
        - When writing instructions, include instructions to ask for the input of the actions in order to run the action.
        - Also use absolutes such as "Must, "Never", or "Always" sparingly -- instead use verbiage that allows more flexibility.
        - In every topic, except for an "Escalation" topic, include an instruction that enables the AI Agent to search knowledge to help the customer with their questions related to the <topic>.

        Provide relevant actions to support the Topic, scope, and instructions.
        ## Rules for actions:
        - Actions are effectively the function that gets invoked to do things for the topic.
        - Actions can have multiple inputs if needed.
        - Outputs represent what properties are sent as a response of the action
        - When writing action descriptions, include in the action description what inputs are needed. Example: "Retrieve the current status and tracking information of a customer's order for a given an orderId"
        - Input descriptions are 1-2 sentences that describe the input and how it is used.
        - Output descriptions are 1-2 sentences that describe the output and how it is used.
        - Action descriptions should provide context of when the action should be used and also what information is needed from the customer.
        - The AI Agent has access to the internet through an action. If there is an action that could be answered through a web search on company's website, such as troubleshooting steps or questions, company policy information, policy guidance, technical support or general company information, then always generate an action called "Knowledge_Lookup".

        # Generate the sample utterances for the agent
        - Generate 4-5 sample utterances for the agent based on the topics and instructions.
        - The sample utterances should tie directly back to an instruction or an action.

        # Generate the description of the agent
        - Generate a 1-2 sentence description of the agent based on the topics and instructions.
        - The description should start with: "You are an AI Agent whose job is to help ...."

        # Always generate some system messages for the agent
        - Generate a System messages, such as welcome and error messages that are sent when your users begin using an agent and if they encounter system errors.
        - The system messages should be in the format of a JSON object with the following fields:
            - name: The name of the system message
            - content: The content of the system message
            - description: The description of the system message

        """

        user_message = f"""Create a complete agent configuration for an agent with these details:
        Description: {description}
        Company Name: {company_name}
        name: {agent_name}
        """

        agent = PydanticAgent(
            model=model, system_message=system_message, output_type=Agent
        )

        result = agent.run_sync(user_message).output
        # Create the modular directory structure
        print("agent_data: ", result)

        # Ensure the required 'domain' field is present in the agent data
        result_dict = result.dict()
        if "domain" not in result_dict:
            result_dict["domain"] = (
                f"https://{company_name.lower().replace(' ', '')}.com"
            )

        AgentUtils.export_agent_to_modular_files(result_dict, output_dir)
        print(f"Successfully generated agent information in {output_dir}")
