"""Exception classes for the Agentforce SDK."""


class AgentforceError(Exception):
    """Base exception for all Agentforce errors."""


class AgentforceAuthError(AgentforceError):
    """Raised when authentication to Salesforce fails."""


class AgentforceApiError(AgentforceError):
    """Raised when there is an error calling an external API."""


class MetadataDeploymentError(AgentforceError):
    """Raised when there is an error deploying metadata to Salesforce."""


class ConfigurationError(AgentforceError):
    """Raised when there is an error with the configuration."""


class ResourceNotFoundError(AgentforceError):
    """Raised when a requested resource is not found."""


class ValidationError(AgentforceError):
    """Raised when validation of input data fails."""
