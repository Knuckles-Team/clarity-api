"""Tests for the dynamic ``clarity_api.__init__`` loading behavior."""

import clarity_api


def test_version_exposed():
    assert isinstance(clarity_api.__version__, str)
    assert clarity_api.__version__


def test_core_members_exposed():
    # Api comes from the eagerly-loaded core api_client module
    assert "Api" in clarity_api.__all__
    assert hasattr(clarity_api, "Api")


def test_optional_availability_flags():
    # These attributes resolve via __getattr__ without raising
    assert isinstance(clarity_api._MCP_AVAILABLE, bool)
    assert isinstance(clarity_api._AGENT_AVAILABLE, bool)


def test_unknown_attribute_raises():
    import pytest

    with pytest.raises(AttributeError):
        _ = clarity_api.this_attribute_does_not_exist
