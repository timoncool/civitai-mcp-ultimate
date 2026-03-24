"""Test fixtures for Civitai MCP Ultimate."""

import pytest

from civitai_mcp_ultimate.client import CivitaiClient


@pytest.fixture
def client():
    """Create a test client (uses CIVITAI_API_KEY from env if available)."""
    return CivitaiClient()
