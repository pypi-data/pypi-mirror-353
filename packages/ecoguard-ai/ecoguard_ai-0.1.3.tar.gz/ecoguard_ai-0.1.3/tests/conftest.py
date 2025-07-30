"""Test configuration and fixtures for EcoGuard AI tests."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from ecoguard_ai.core.analyzer import AnalysisConfig, EcoGuardAnalyzer


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_python_file(temp_dir: Path) -> Path:
    """Create a sample Python file for testing."""
    content = '''
"""Sample Python file for testing."""

def add_numbers(a, b):
    """Add two numbers together."""
    result = a + b
    return result

def unused_function():
    """This function is never called."""
    pass

class Calculator:
    def __init__(self):
        self.value = 0

    def add(self, num):
        self.value += num
        return self.value

# Some inefficient string concatenation
text = ""
for i in range(10):
    text = text + str(i)

print("Hello, World!")
'''

    file_path = temp_dir / "sample.py"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def analyzer() -> EcoGuardAnalyzer:
    """Create a basic analyzer instance."""
    config = AnalysisConfig()
    return EcoGuardAnalyzer(config)


@pytest.fixture
def minimal_analyzer() -> EcoGuardAnalyzer:
    """Create an analyzer with all modules disabled (for testing core functionality)."""
    config = AnalysisConfig(
        enable_quality=False,
        enable_security=False,
        enable_green=False,
        enable_ai_code=False,
    )
    return EcoGuardAnalyzer(config)
