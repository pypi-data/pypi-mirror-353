"""
Basic tests that should always pass
"""


def test_basic_python():
    """Test that basic Python functionality works"""
    assert 1 + 1 == 2
    assert "hello".upper() == "HELLO"
    assert [1, 2, 3][1] == 2


def test_imports_work():
    """Test that basic imports work"""
    import os
    import sys
    import json
    assert os.path.exists(__file__)
    assert sys.version_info.major == 3


def test_pytest_works():
    """Test that pytest itself is working"""
    import pytest
    assert pytest.__version__ is not None
