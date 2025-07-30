"""Attribute Mapping models for AgentForce SDK."""

from typing import Dict, Literal

from pydantic import BaseModel, ConfigDict, Field

from agent_sdk.models.variable import Variable


class AttributeMapping(BaseModel):
    """Maps action parameters to agent variables."""
    
    action_parameter: str = Field(..., description="Name of the action parameter (input or output)")
    variable: Variable = Field(..., description="Agent variable to map to/from")
    direction: Literal["input", "output"] = Field(..., description="Direction of mapping (input to action or output from action)")
    
    model_config = ConfigDict(extra="allow")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = self.model_dump(exclude_none=True)
        # Convert variable to dictionary for serialization
        if "variable" in data and isinstance(self.variable, Variable):
            data["variable"] = self.variable.to_dict()
        return data
        
    @classmethod
    def from_dict(cls, data: Dict) -> "AttributeMapping":
        """Create from dictionary."""
        # Convert variable dictionary back to Variable object
        if "variable" in data and isinstance(data["variable"], dict):
            data["variable"] = Variable.from_dict(data["variable"])
        return cls.model_validate(data) 