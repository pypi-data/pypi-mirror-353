"""
Tests for schema validation
"""

import pytest
from pydantic import ValidationError

from astk.schema import (
    PersonaConfig,
    BudgetConfig,
    SuccessCriteria,
    ChaosConfig,
    ScenarioConfig
)


def test_persona_config_validation():
    """Test PersonaConfig validation"""
    # Valid config
    config = PersonaConfig(
        archetype="impatient_mobile_user",
        temperature=0.9,
        traits=["demanding", "tech-savvy"]
    )
    assert config.archetype == "impatient_mobile_user"
    assert config.temperature == 0.9
    assert config.traits == ["demanding", "tech-savvy"]

    # Invalid temperature
    with pytest.raises(ValidationError):
        PersonaConfig(
            archetype="test",
            temperature=1.5
        )


def test_budget_config_validation():
    """Test BudgetConfig validation"""
    # Valid config
    config = BudgetConfig(
        latency_ms=3000,
        cost_usd=0.1,
        tokens=1000
    )
    assert config.latency_ms == 3000
    assert config.cost_usd == 0.1
    assert config.tokens == 1000

    # All fields optional
    config = BudgetConfig()
    assert config.latency_ms is None
    assert config.cost_usd is None
    assert config.tokens is None


def test_success_criteria_validation():
    """Test SuccessCriteria validation"""
    # Valid config
    config = SuccessCriteria(
        regex="(?i)here's",
        semantic_score=0.8,
        task_specific={"exact_match": True}
    )
    assert config.regex == "(?i)here's"
    assert config.semantic_score == 0.8
    assert config.task_specific == {"exact_match": True}

    # Invalid semantic score
    with pytest.raises(ValidationError):
        SuccessCriteria(semantic_score=1.5)


def test_chaos_config_validation():
    """Test ChaosConfig validation"""
    # Valid config
    config = ChaosConfig(
        drop_tool=["search", "memory"],
        inject_latency=[500, 1000],
        malform_messages=True
    )
    assert config.drop_tool == ["search", "memory"]
    assert config.inject_latency == [500, 1000]
    assert config.malform_messages is True


def test_scenario_config_validation(sample_scenario_config):
    """Test ScenarioConfig validation"""
    # Valid config from fixture
    assert sample_scenario_config.task == "file_qna"
    assert sample_scenario_config.protocol == "A2A"

    # Invalid protocol
    with pytest.raises(ValidationError):
        ScenarioConfig(
            task="test",
            persona={"archetype": "test", "temperature": 0.7},
            protocol="INVALID",
            success={}
        )
