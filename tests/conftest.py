"""Test configuration."""

import pytest


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment for each test."""
    yield
    # Cleanup after test if needed
