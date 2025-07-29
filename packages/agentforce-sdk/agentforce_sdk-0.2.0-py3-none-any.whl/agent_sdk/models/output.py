"""Output model for agent actions."""

import warnings

# Forward the Output class from action.py
from agent_sdk.models.action import Output

# Issue a deprecation warning
warnings.warn(
    "Importing Output from agent_sdk.models.output is deprecated. "
    "Please import from agent_sdk.models.action or agent_sdk.models instead.",
    DeprecationWarning,
    stacklevel=2
)
