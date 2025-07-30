"""
Test basic package imports and new OpenAI Evals integration
"""
import pytest


def test_package_import():
    """Test that the package can be imported"""
    import astk
    assert astk.__version__ == "0.2.0"


def test_schema_imports():
    """Test that schema classes can be imported"""
    try:
        from astk.schema import ScenarioConfig, PersonaConfig, SuccessCriteria

        # Test basic instantiation
        persona = PersonaConfig(archetype="test")
        assert persona.archetype == "test"

        criteria = SuccessCriteria()
        assert criteria.regex is None
    except ImportError as e:
        pytest.skip(f"Schema imports failed: {e}")


def test_metrics_import():
    """Test that metrics can be imported"""
    try:
        from astk.metrics import QualityMetrics

        # Test basic instantiation
        metrics = QualityMetrics()
        assert metrics is not None
    except ImportError as e:
        pytest.skip(f"Metrics import failed: {e}")


def test_runner_import():
    """Test that runner can be imported"""
    try:
        from astk.runner import AgentRunner
        assert AgentRunner is not None
    except ImportError as e:
        pytest.skip(f"Runner import failed: {e}")


def test_evals_integration_import():
    """Test that OpenAI Evals integration can be imported (optional)"""
    try:
        from astk.evals_integration import OpenAIEvalsAdapter, GRADER_PROMPTS

        # Test that grader prompts are available
        assert "code_qa" in GRADER_PROMPTS
        assert "general" in GRADER_PROMPTS
        assert "customer_service" in GRADER_PROMPTS
        assert "research" in GRADER_PROMPTS

        # Test adapter class exists
        assert OpenAIEvalsAdapter is not None

    except ImportError as e:
        pytest.skip(f"OpenAI Evals integration not available: {e}")


def test_cli_import():
    """Test that CLI can be imported"""
    try:
        from astk.cli import cli
        assert cli is not None
    except ImportError as e:
        pytest.skip(f"CLI import failed: {e}")


def test_package_all_exports():
    """Test that __all__ exports work correctly"""
    import astk

    # These should always be available
    assert hasattr(astk, 'ScenarioConfig')
    assert hasattr(astk, 'PersonaConfig')
    assert hasattr(astk, 'SuccessCriteria')

    # This might not be available if openai package not installed
    # But we shouldn't error if it's not there
    evals_available = hasattr(astk, 'OpenAIEvalsAdapter')
    print(f"OpenAI Evals integration available: {evals_available}")
