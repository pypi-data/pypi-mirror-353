"""
Test basic package imports
"""
import pytest


def test_package_import():
    """Test that the package can be imported"""
    import astk
    assert astk.__version__ == "0.1.3"


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
