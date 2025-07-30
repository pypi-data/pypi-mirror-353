"""
ASTK - AgentSprint TestKit
Professional AI agent evaluation and testing framework with OpenAI Evals integration
"""

__version__ = "0.2.0"
__author__ = "ASTK Team"
__email__ = "admin@blackbox-dev.com"

from .schema import (
    ScenarioConfig,
    PersonaConfig,
    SuccessCriteria
)

# Optional OpenAI Evals integration
try:
    from .evals_integration import OpenAIEvalsAdapter
    __all__ = ["ScenarioConfig", "PersonaConfig",
               "SuccessCriteria", "OpenAIEvalsAdapter"]
except ImportError:
    __all__ = ["ScenarioConfig", "PersonaConfig", "SuccessCriteria"]
