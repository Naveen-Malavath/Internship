"""
Pytest configuration and shared fixtures for styling system tests.
"""

import logging
import os
from pathlib import Path

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def output_dir():
    """Create output directory for test results."""
    output_path = Path("tests/output/styling_tests")
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Test output directory: {output_path.absolute()}")
    return output_path


@pytest.fixture(scope="function")
def test_results():
    """Store test results for comparison."""
    return []


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    # Set test output directory if not already set
    if "TEST_OUTPUT_DIR" not in os.environ:
        output_dir = Path("tests/output/styling_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("TEST_OUTPUT_DIR", str(output_dir.absolute()))
    
    # Disable API calls in tests (use mocks if needed)
    # monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    
    logger.debug("Test environment set up")

