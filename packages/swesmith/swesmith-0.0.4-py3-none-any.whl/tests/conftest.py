"""
Common pytest fixtures and configuration for SWE-smith tests.
"""

import os
import pytest
import sys

from pathlib import Path


# Add the repository root to the Python path to ensure imports work correctly
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


@pytest.fixture
def test_file_go():
    return Path(repo_root) / "tests/test_logs/files/file.go"


@pytest.fixture
def test_file_py():
    return Path(repo_root) / "tests/test_logs/files/file.py"


@pytest.fixture
def test_output_gotest():
    return (
        Path(repo_root)
        / "tests/test_logs/test_output/gin-gonic__gin.3c12d2a8.lm_rewrite__4pb48n1g.txt"
    )


@pytest.fixture
def test_output_pytest():
    return (
        Path(repo_root)
        / "tests/test_logs/test_output/django-money__django-money.835c1ab8.combine_file__7znr0kum.txt"
    )


@pytest.fixture
def logs_trajectories():
    return Path(repo_root) / "tests/test_logs/trajectories"


@pytest.fixture
def logs_run_evaluation():
    return Path(repo_root) / "tests/test_logs/run_evaluation"


@pytest.fixture
def logs_run_validation():
    return Path(repo_root) / "tests/test_logs/run_validation"


@pytest.fixture
def ft_xml_example():
    return Path(repo_root) / "tests/test_logs/ft_xml_example.jsonl"


@pytest.fixture
def task_instance_path():
    return Path(repo_root) / "tests/test_logs/pandas-dev__pandas.95280573.pr_53652.json"
