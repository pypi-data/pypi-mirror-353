"""
AgentSprint TestKit (ASTK) - A CI-first behavioural-coverage and regression-gating framework
"""

__version__ = "0.1.3"

# Import main classes for easier access
try:
    from .schema import ScenarioConfig, PersonaConfig, SuccessCriteria
    from .metrics import QualityMetrics
    from .runner import AgentRunner
except ImportError:
    # Allow package to be imported even if dependencies aren't installed
    pass
