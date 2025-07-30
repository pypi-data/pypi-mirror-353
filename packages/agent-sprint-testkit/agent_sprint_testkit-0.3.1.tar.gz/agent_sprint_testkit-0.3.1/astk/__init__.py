"""
AgentSprint TestKit (ASTK) - Professional AI Agent Evaluation
"""

__version__ = "0.3.0"
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
