"""Variable models."""

from typing import Any, Dict, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Variable(BaseModel):
    """Variable class for agent."""

    name: str = Field(..., description="Name of the variable")
    value: Any = Field(None, description="Value of the variable")
    description: str = Field("", description="Description of the variable")
    
    # Fields for Salesforce conversation variables
    data_type: str = Field("String", description="Data type of the variable (String, Text, Number, Boolean, etc.)")
    label: Optional[str] = Field(None, description="Label for the variable in Salesforce")
    include_in_prompt: bool = Field(False, description="Whether to include this variable in the prompt")
    visibility: Literal["Internal", "External"] = Field("Internal", description="Visibility of the variable")
    var_type: Literal["custom", "conversation"] = Field("custom", description="Variable type")
    developer_name: Optional[str] = Field(None, description="Developer name used in Salesforce metadata")

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values and ensure field integrity."""
        if isinstance(data, dict):
            # Set developer_name to name if not provided
            if "name" in data and (not data.get("developer_name") or data.get("developer_name") is None):
                data["developer_name"] = data["name"]
                
            # Set label to name if not provided
            if "name" in data and (not data.get("label") or data.get("label") is None):
                data["label"] = data["name"]

        return data

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = self.model_dump(exclude_none=True)
        # Convert data_type to dataType for serialization consistency
        if "data_type" in data:
            data["dataType"] = data.pop("data_type")
        if "var_type" in data:
            data["varType"] = data.pop("var_type")
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Variable":
        """Create from dictionary."""
        return cls.model_validate(data)
