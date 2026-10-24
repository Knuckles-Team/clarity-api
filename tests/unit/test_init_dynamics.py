"""Tests for the dynamic ``clarity_api.__init__`` loading behavior.

Covers ``CONCEPT:CY-OS.governance.package-server-bootstrap`` (Package & Server Bootstrap).
"""

import pytest

import clarity_api


@pytest.mark.concept("CY-OS.governance.package-server-bootstrap")
def test_concept_cla_005_core_members_exposed():
    """CLA-005: the eagerly-loaded ``Api`` member is exported."""
    assert "Api" in clarity_api.__all__
    assert hasattr(clarity_api, "Api")




@pytest.mark.concept("CY-OS.governance.package-server-bootstrap")
def test_concept_cla_005_unknown_attribute_raises():
    """CLA-005: unknown attribute access raises ``AttributeError``."""
    with pytest.raises(AttributeError):
        _ = clarity_api.this_attribute_does_not_exist
