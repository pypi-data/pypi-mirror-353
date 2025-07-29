"""Action models for AgentForce SDK."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from agent_sdk.models.attribute_mapping import AttributeMapping
from agent_sdk.models.variable import Variable


class Input(BaseModel):
    """Input parameter for an action."""

    name: str = Field(..., description="Name of the input parameter")
    description: str = Field("", description="Description of the input parameter")
    data_type: str = Field("String", description="Data type of the input parameter")
    required: bool = Field(True, description="Whether the input parameter is required")

    model_config = ConfigDict(extra="allow")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump(exclude_none=True)
        # Convert data_type to dataType for serialization
        if "data_type" in data:
            data["dataType"] = data.pop("data_type")
        return data


class Output(BaseModel):
    """Output parameter or response from an action."""

    name: Optional[str] = Field(None, description="Name of the output parameter")
    description: Optional[str] = Field(
        None, description="Description of the output parameter"
    )
    data_type: Optional[str] = Field(
        None, description="Data type of the output parameter"
    )
    required: Optional[bool] = Field(
        None, description="Whether the output parameter is required"
    )

    # Example output fields
    status: Optional[str] = Field(None, description="Status of the example output")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Details of the example output"
    )

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_output(self) -> "Output":
        """Validate the output based on its usage."""
        # Parameter definition mode - requires name
        param_fields = [self.name, self.description, self.data_type]
        # Example output mode - requires status
        example_fields = [self.status, self.details]

        if any(param_fields) and not self.name:
            raise ValueError("When used as a parameter definition, 'name' is required")

        if any(example_fields) and not self.status:
            raise ValueError("When used as an example output, 'status' is required")

        # Set defaults for parameter definition mode
        if self.name and self.description is None:
            self.description = ""

        if self.name and self.data_type is None:
            self.data_type = "String"

        if self.name and self.required is None:
            self.required = True

        return self

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Output":
        """Create from dictionary.

        Supports both parameter definition and example output formats.
        """
        if isinstance(data, dict):
            # If has status, it's an example output format
            if "status" in data:
                return cls(status=data.get("status"), details=data.get("details"))
            # Otherwise, it's a parameter definition
            return cls.model_validate(data)
        return cls.model_validate(data)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump(exclude_none=True)
        # Convert data_type to dataType for serialization if this is a parameter definition
        if "data_type" in data:
            data["dataType"] = data.pop("data_type")
        return data


class Action(BaseModel):
    """Action class for agent."""

    name: str = Field(..., description="Name of the action")
    description: str = Field(..., description="Description of the action")
    inputs: List[Input] = Field(
        default_factory=list, description="List of input parameters"
    )
    outputs: List[Output] = Field(
        default_factory=list, description="List of output parameters"
    )
    example_output: Optional[Dict[str, Any]] = Field(
        None, description="Example output for the action"
    )
    attribute_mappings: List[AttributeMapping] = Field(
        default_factory=list, description="Mappings between action parameters and agent variables"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_action(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate action data and convert example_output if needed."""
        if isinstance(data, dict):
            # Set default example_output if not provided
            if "example_output" not in data or data["example_output"] is None:
                data["example_output"] = {"status": "success"}
            # If example_output is an Output object, convert it to dict
            elif isinstance(data["example_output"], Output):
                output = data["example_output"]
                result = {"status": output.status or "success"}
                if output.details:
                    result.update(output.details)
                data["example_output"] = result
        return data

    model_config = ConfigDict(extra="allow")

    def add_input(
        self,
        input_param: Union[
            Input, Dict[str, Any], str, List[Union[Input, Dict[str, Any]]]
        ],
        description: str = "",
        data_type: str = "String",
        required: bool = True,
    ) -> None:
        """Add one or more input parameters to the action.

        This method supports multiple call signatures for backward compatibility:
        - add_input(Input): Add a single Input object
        - add_input(dict): Add a single input from a dictionary
        - add_input(name, description, data_type, required): Add an input with parameters
        - add_input([Input, ...]): Add multiple Input objects
        - add_input([dict, ...]): Add multiple inputs from dictionaries
        """
        # Handle single Input object
        if isinstance(input_param, Input):
            self.inputs.append(input_param)
        # Handle single dictionary
        elif isinstance(input_param, dict):
            self.inputs.append(Input.model_validate(input_param))
        # Handle string as name with additional parameters
        elif isinstance(input_param, str):
            self.inputs.append(
                Input(
                    name=input_param,
                    description=description,
                    data_type=data_type,
                    required=required,
                )
            )
        # Handle list of inputs
        elif isinstance(input_param, list):
            for param in input_param:
                if isinstance(param, Input):
                    self.inputs.append(param)
                elif isinstance(param, dict):
                    self.inputs.append(Input.model_validate(param))
                else:
                    raise TypeError(
                        "Each input parameter must be an Input instance or dictionary"
                    )
        else:
            raise TypeError(
                "input_param must be an Input instance, dictionary, string, or list of either"
            )

    def add_output(
        self,
        output_param: Union[
            Output, Dict[str, Any], str, List[Union[Output, Dict[str, Any]]]
        ],
        description: str = "",
        data_type: str = "String",
        required: bool = True,
    ) -> None:
        """Add one or more output parameters to the action.

        This method supports multiple call signatures for backward compatibility:
        - add_output(Output): Add a single Output object
        - add_output(dict): Add a single output from a dictionary
        - add_output(name, description, data_type, required): Add an output with parameters
        - add_output([Output, ...]): Add multiple Output objects
        - add_output([dict, ...]): Add multiple outputs from dictionaries
        """
        # Handle single Output object
        if isinstance(output_param, Output):
            self.outputs.append(output_param)
        # Handle single dictionary
        elif isinstance(output_param, dict):
            self.outputs.append(Output.model_validate(output_param))
        # Handle string as name with additional parameters
        elif isinstance(output_param, str):
            self.outputs.append(
                Output(
                    name=output_param,
                    description=description,
                    data_type=data_type,
                    required=required,
                )
            )
        # Handle list of outputs
        elif isinstance(output_param, list):
            for param in output_param:
                if isinstance(param, Output):
                    self.outputs.append(param)
                elif isinstance(param, dict):
                    self.outputs.append(Output.model_validate(param))
                else:
                    raise TypeError(
                        "Each output parameter must be an Output instance or dictionary"
                    )
        else:
            raise TypeError(
                "output_param must be an Output instance, dictionary, string, or list of either"
            )

    def set_example_output(self, output: Union[Output, Dict[str, Any]]) -> None:
        """Set the example output for the action."""
        if isinstance(output, Output):
            # Convert Output object to dict format
            result = {"status": output.status}
            if output.details:
                for key, value in output.details.items():
                    result[key] = value
            self.example_output = result
        elif isinstance(output, dict):
            self.example_output = output
        else:
            raise TypeError("output must be an Output instance or dictionary")

    def map_input(self, parameter_name: str, variable: Variable) -> None:
        """Map an input parameter to an agent variable."""
        self.attribute_mappings.append(
            AttributeMapping(
                action_parameter=parameter_name,
                variable=variable,
                direction="input"
            )
        )
        
    def map_output(self, parameter_name: str, variable: Variable) -> None:
        """Map an output parameter to an agent variable."""
        self.attribute_mappings.append(
            AttributeMapping(
                action_parameter=parameter_name,
                variable=variable,
                direction="output"
            )
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = self.model_dump(exclude_none=True)
        
        # Convert lists of objects to lists of dictionaries
        if "inputs" in data:
            data["inputs"] = [input_obj.to_dict() for input_obj in self.inputs]
            
        if "outputs" in data:
            data["outputs"] = [output_obj.to_dict() for output_obj in self.outputs]
            
        if "attribute_mappings" in data:
            data["attribute_mappings"] = [mapping.to_dict() for mapping in self.attribute_mappings]
            
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Action":
        """Create from dictionary."""
        if isinstance(data, dict):
            # Extract objects to create proper models
            inputs_data = data.pop("inputs", [])
            outputs_data = data.pop("outputs", [])
            attribute_mappings_data = data.pop("attribute_mappings", [])
            
            action = cls(**data)
            
            # Add inputs
            for input_data in inputs_data:
                if isinstance(input_data, dict):
                    action.add_input(input_data)
                else:
                    action.add_input(input_data)
                    
            # Add outputs
            for output_data in outputs_data:
                if isinstance(output_data, dict):
                    action.add_output(output_data)
                else:
                    action.add_output(output_data)
                    
            # Add attribute mappings
            for mapping_data in attribute_mappings_data:
                if isinstance(mapping_data, dict):
                    action.attribute_mappings.append(AttributeMapping.from_dict(mapping_data))
                else:
                    action.attribute_mappings.append(mapping_data)
                    
            return action
        return cls.model_validate(data)
