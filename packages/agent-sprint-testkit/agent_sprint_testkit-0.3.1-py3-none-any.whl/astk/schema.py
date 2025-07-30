"""
ASTK Schema definitions
Enhanced for multi-layer evaluation support in v0.2.0
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class PersonaConfig(BaseModel):
    """Configuration for agent persona during testing"""
    archetype: str = Field(
        description="Persona archetype (e.g., 'senior_developer')")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Response creativity/randomness")
    traits: Optional[List[str]] = Field(
        default_factory=list, description="Personality traits for the persona"
    )


class OpenAIEvaluationConfig(BaseModel):
    """Configuration for a single OpenAI evaluation layer"""
    evaluator: str = Field(
        description="OpenAI model to use as evaluator (e.g., 'gpt-4', 'o1-preview')")
    prompt: str = Field(
        description="Evaluation prompt with criteria and instructions")
    pass_threshold: float = Field(
        default=7.0, ge=0.0, le=10.0, description="Minimum score to pass this evaluation")
    weight: Optional[float] = Field(
        default=1.0, ge=0.0, description="Weight of this evaluation in overall score")
    evaluation_type: Optional[str] = Field(
        default="general", description="Type of evaluation (general, security, ethics, etc.)")
    timeout_seconds: Optional[int] = Field(
        default=30, description="Timeout for this evaluation")
    retry_attempts: Optional[int] = Field(
        default=2, description="Number of retry attempts on failure")


class SuccessCriteria(BaseModel):
    """Enhanced success criteria for scenario validation with multi-layer support"""
    regex: Optional[str] = Field(
        None, description="Regex pattern to match in response")
    semantic_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Min semantic similarity score"
    )
    task_specific: Optional[Dict[str, Any]] = Field(
        None, description="Task-specific success criteria")

    # Multi-layer OpenAI evaluation support
    openai_evaluations: Optional[List[OpenAIEvaluationConfig]] = Field(
        default_factory=list, description="List of OpenAI evaluation configurations"
    )

    # Overall evaluation settings
    require_all_evaluations_pass: bool = Field(
        default=True, description="Whether all OpenAI evaluations must pass"
    )
    overall_pass_threshold: float = Field(
        default=7.0, ge=0.0, le=10.0, description="Overall weighted score threshold"
    )

    # Advanced evaluation options
    evaluation_weights: Optional[Dict[str, float]] = Field(
        default_factory=dict, description="Custom weights for different evaluation layers"
    )
    fail_fast: bool = Field(
        default=False, description="Stop evaluation on first failure"
    )


class ChaosConfig(BaseModel):
    """Configuration for chaos engineering during testing"""
    drop_tool: Optional[List[str]] = Field(
        default_factory=list, description="Tools to randomly drop/disable"
    )
    inject_latency: Optional[List[int]] = Field(
        default_factory=list, description="Latency values (ms) to randomly inject"
    )
    malform_messages: bool = Field(
        default=False, description="Randomly malform input messages"
    )

    # Enhanced chaos options for rigorous testing
    adversarial_prompts: bool = Field(
        default=False, description="Inject adversarial prompt attempts"
    )
    memory_pressure: bool = Field(
        default=False, description="Simulate memory pressure conditions"
    )
    network_instability: bool = Field(
        default=False, description="Simulate network connectivity issues"
    )
    resource_constraints: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Resource constraint configurations"
    )


class BudgetConfig(BaseModel):
    """Resource budget constraints for scenario execution"""
    latency_ms: Optional[int] = Field(
        None, description="Maximum latency in milliseconds")
    cost_usd: Optional[float] = Field(None, description="Maximum cost in USD")
    tokens: Optional[int] = Field(None, description="Maximum token usage")

    # Enhanced budget controls
    evaluation_cost_usd: Optional[float] = Field(
        None, description="Maximum cost for evaluation layers"
    )
    retry_budget: Optional[int] = Field(
        default=3, description="Maximum number of retries allowed"
    )
    timeout_budget_ms: Optional[int] = Field(
        None, description="Total timeout budget including retries"
    )


class ScenarioConfig(BaseModel):
    """Enhanced scenario configuration with multi-layer evaluation support"""
    # Core scenario identification
    name: Optional[str] = Field(None, description="Unique scenario name")
    task: str = Field(description="Task type identifier")
    description: Optional[str] = Field(
        None, description="Human-readable scenario description")

    # Scenario metadata
    difficulty: Optional[str] = Field(
        default="intermediate",
        description="Difficulty level: beginner, intermediate, advanced, expert"
    )
    category: Optional[str] = Field(
        default="general",
        description="Scenario category for organization and analysis"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list, description="Additional tags for categorization"
    )

    # Core configuration
    persona: PersonaConfig = Field(description="Agent persona configuration")
    protocol: str = Field(description="Communication protocol")
    success: SuccessCriteria = Field(description="Success validation criteria")

    # Input specification
    input_prompt: Optional[str] = Field(
        None, description="Specific input prompt for this scenario")
    input_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional input data for the scenario"
    )

    # Resource management
    budgets: Optional[BudgetConfig] = Field(
        None, description="Resource budget constraints")
    chaos: Optional[ChaosConfig] = Field(
        None, description="Chaos engineering configuration")

    # Evaluation metadata
    estimated_duration_ms: Optional[int] = Field(
        None, description="Estimated execution time"
    )
    priority: Optional[int] = Field(
        default=1, description="Scenario priority for execution ordering"
    )

    # Versioning and tracking
    version: Optional[str] = Field(
        default="1.0", description="Scenario version")
    created_by: Optional[str] = Field(None, description="Scenario creator")
    last_modified: Optional[str] = Field(
        None, description="Last modification timestamp")


class EvaluationResult(BaseModel):
    """Results from scenario evaluation"""
    scenario_name: str
    passed: bool
    overall_score: float
    layer_results: Dict[str, Any]
    execution_time_ms: int
    cost_usd: float
    tokens_used: int

    # Detailed feedback
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    # Metadata
    timestamp: str
    evaluator_versions: Dict[str, str] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class BenchmarkSuite(BaseModel):
    """Collection of scenarios for comprehensive evaluation"""
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    scenarios: List[ScenarioConfig]

    # Suite metadata
    total_estimated_cost_usd: Optional[float] = None
    total_estimated_time_minutes: Optional[int] = None
    difficulty_distribution: Optional[Dict[str, int]] = None
    category_coverage: Optional[List[str]] = None

    # Evaluation configuration
    parallel_execution: bool = Field(
        default=False, description="Allow parallel scenario execution")
    max_retries: int = Field(
        default=2, description="Maximum retries per scenario")
    timeout_minutes: int = Field(
        default=60, description="Total benchmark timeout")

    # Quality assurance
    min_pass_rate: float = Field(
        default=0.7, description="Minimum pass rate for suite success")
    required_categories: Optional[List[str]] = Field(
        default_factory=list, description="Categories that must have passing scenarios"
    )


class AgentConfig(BaseModel):
    """Configuration for the agent being tested"""
    name: str
    version: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # Capabilities and constraints
    supported_tools: Optional[List[str]] = Field(default_factory=list)
    max_context_tokens: Optional[int] = None
    rate_limits: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # Testing metadata
    baseline_performance: Optional[Dict[str, float]] = Field(
        default_factory=dict)
    known_limitations: Optional[List[str]] = Field(default_factory=list)


class TestSession(BaseModel):
    """Complete test session with results and metadata"""
    session_id: str
    agent_config: AgentConfig
    benchmark_suite: BenchmarkSuite

    # Results
    scenario_results: List[EvaluationResult]
    overall_pass_rate: float
    total_cost_usd: float
    total_duration_ms: int

    # Session metadata
    start_time: str
    end_time: Optional[str] = None
    environment: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # Analysis
    category_performance: Dict[str, float] = Field(default_factory=dict)
    difficulty_performance: Dict[str, float] = Field(default_factory=dict)
    recommendation_summary: List[str] = Field(default_factory=list)
