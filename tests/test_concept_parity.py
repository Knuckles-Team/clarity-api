"""Concept-parity tests for clarity-api.

1. Every ``CONCEPT:CLA-*`` tag used in tool docstrings/source must be documented
   in ``docs/concepts.md``.
2. Every agent-utilities 5-Pillar concept referenced locally must be registered
   in the master ``agent-utilities/docs/overview.md`` registry.
"""

import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.dirname(os.path.dirname(ROOT_DIR))
MASTER_OVERVIEW_PATH = os.path.join(
    WORKSPACE_DIR, "agent-utilities", "docs", "overview.md"
)
CONCEPTS_DOC = os.path.join(ROOT_DIR, "docs", "concepts.md")


def _extract_concepts_from_codebase(directory):
    found = set()
    for root, _, files in os.walk(directory):
        if any(
            seg in root
            for seg in ("node_modules", ".venv", ".git", "__pycache__")
        ):
            continue
        for file in files:
            if file.endswith((".py", ".md")):
                try:
                    with open(os.path.join(root, file), encoding="utf-8") as f:
                        found.update(
                            re.findall(r"CONCEPT:([A-Z]+-\d+(?:\.\d+)?)", f.read())
                        )
                except Exception:
                    pass
    return found


def _extract_concepts_from_overview(filepath):
    if not os.path.exists(filepath):
        return set()
    concepts = set()
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            if not line.strip().startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                raw_id = parts[1].replace("*", "").strip()
                if re.match(r"^[A-Z]+-\d+(?:\.\d+)?$", raw_id):
                    concepts.add(raw_id)
    return concepts


def test_local_concepts_documented():
    """Every CLA-* concept used in code must appear in docs/concepts.md."""
    with open(CONCEPTS_DOC, encoding="utf-8") as f:
        documented = set(re.findall(r"CONCEPT:(CLA-\d+)", f.read()))

    used = {c for c in _extract_concepts_from_codebase(ROOT_DIR) if c.startswith("CLA-")}
    missing = used - documented
    assert not missing, (
        f"CLA concepts used in code but not documented in docs/concepts.md: {missing}"
    )


def test_concept_parity_with_master_registry():
    """Every agent-utilities pillar concept used locally must be registered upstream."""
    master = _extract_concepts_from_overview(MASTER_OVERVIEW_PATH)
    pillars = ("ORCH-", "KG-", "AHE-", "ECO-", "OS-")
    local = {
        c
        for c in _extract_concepts_from_codebase(ROOT_DIR)
        if c.startswith(pillars) and not c.startswith("KG-00")
    }
    unregistered = local - master
    assert not unregistered, (
        f"Concepts used in clarity-api but NOT registered in the master "
        f"agent-utilities/docs/overview.md registry: {unregistered}"
    )
