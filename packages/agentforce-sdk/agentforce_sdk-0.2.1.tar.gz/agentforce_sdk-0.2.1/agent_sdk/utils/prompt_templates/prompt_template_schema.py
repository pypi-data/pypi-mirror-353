"""Pydantic models for prompt template schema."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SalesforceMapping(BaseModel):
    """Salesforce object and field mapping for an input field."""

    object: str = Field(description="The Salesforce object name")
    field: str = Field(description="The Salesforce field name")
    relationship_field: Optional[str] = Field(
        None, description="Optional relationship field name"
    )


class ApexAction(BaseModel):
    """Configuration for an Apex action to query related data."""

    name: str = Field(
        description="Name of the Apex action, e.g., GetAccountRecentOpportunities"
    )
    description: str = Field(description="What this action queries")
    parent_object: str = Field(description="Parent Salesforce object, e.g., Account")
    query_type: str = Field(description="Type of query, e.g., RecentOpportunities")


class PromptTemplateInput(BaseModel):
    """Input field for a prompt template."""

    name: str = Field(description="Field name")
    data_type: str = Field(description="Data type (string, number, boolean, etc.)")
    description: str = Field(description="Description of what this field represents")
    required: bool = Field(description="Whether this field is required")
    is_sobject_field: Optional[bool] = Field(
        False, description="Indicates if this is a Salesforce object field"
    )
    salesforce_mapping: Optional[SalesforceMapping] = Field(
        None, description="Salesforce mapping if is_sobject_field is true"
    )
    requires_apex_query: Optional[bool] = Field(
        False, description="Set to true if this field needs an Apex action"
    )
    apex_action: Optional[ApexAction] = Field(
        None, description="Apex action configuration if requires_apex_query is true"
    )


class PromptTemplateSchema(BaseModel):
    """Schema for generating prompt templates."""

    inputs: List[PromptTemplateInput] = Field(description="List of input fields")
    prompt_template: str = Field(
        description="Natural language prompt with field placeholders"
    )
    instructions: List[str] = Field(
        description="Specific instructions based on the task"
    )
