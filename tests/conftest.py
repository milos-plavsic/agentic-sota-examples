"""Pytest configuration."""

import pytest


@pytest.fixture
def tmp_cache_dir(tmp_path):
    """Temporary cache directory."""
    return tmp_path / "cache"


@pytest.fixture
def sample_data():
    """Sample test data."""
    return {
        "url": "https://example.com/data",
        "data": {"key": "value"},
    }
