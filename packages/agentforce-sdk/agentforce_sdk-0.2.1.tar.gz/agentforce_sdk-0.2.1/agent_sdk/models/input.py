"""Input model for agent actions."""

import warnings

# Forward the Input class from action.py
from agent_sdk.models.action import Input

# Issue a deprecation warning
warnings.warn(
    "Importing Input from agent_sdk.models.input is deprecated. "
    "Please import from agent_sdk.models.action or agent_sdk.models instead.",
    DeprecationWarning,
    stacklevel=2
)
