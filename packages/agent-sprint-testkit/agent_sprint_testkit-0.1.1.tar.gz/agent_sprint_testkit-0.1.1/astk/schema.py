"""
Pydantic models for ASTK scenario configuration
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, constr


class PersonaConfig(BaseModel):
    """Configuration for synthetic persona generation"""
    archetype: str = Field(..., description="Persona archetype name")
    temperature: float = Field(
        0.7, ge=0.0, le=1.0, description="Sampling temperature")
    traits: Optional[List[str]] = Field(
        None, description="Additional persona traits")


class BudgetConfig(BaseModel):
    """Resource budget constraints"""
    latency_ms: Optional[int] = Field(
        None, description="Max latency in milliseconds")
    cost_usd: Optional[float] = Field(None, description="Max cost in USD")
    tokens: Optional[int] = Field(None, description="Max token usage")


class SuccessCriteria(BaseModel):
    """Success criteria for scenario validation"""
    regex: Optional[str] = Field(
        None, description="Regex pattern to match in response")
    semantic_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Min semantic similarity score"
    )
    task_specific: Optional[dict] = Field(
        None, description="Task-specific success criteria")


class ChaosConfig(BaseModel):
    """Chaos testing configuration"""
    drop_tool: Optional[List[str]] = Field(
        None, description="Tools to simulate failures for")
    inject_latency: Optional[List[int]] = Field(
        None, description="Latency values to inject (ms)")
    malform_messages: Optional[bool] = Field(
        False, description="Inject malformed messages")


class ScenarioConfig(BaseModel):
    """Top-level scenario configuration"""
    task: str = Field(..., description="Task identifier")
    persona: PersonaConfig
    protocol: constr(regex="^(A2A|REST|GRPC)$") = Field(...,
                                                        description="Agent protocol")
    success: SuccessCriteria
    budgets: Optional[BudgetConfig] = None
    chaos: Optional[Union[List[str], ChaosConfig]] = None

    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "task": "file_qna",
                "persona": {
                    "archetype": "impatient_mobile_user",
                    "temperature": 0.9
                },
                "protocol": "A2A",
                "success": {
                    "regex": "(?i)here's"
                },
                "budgets": {
                    "latency_ms": 3000
                },
                "chaos": [
                    "drop_tool:search",
                    "inject_latency:1500"
                ]
            }
        }
