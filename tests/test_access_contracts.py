"""CONN-CLARITY-API-CONNECTOR-CONTENT-R002: competency reads declare access contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from scion_sdk.access_contract import parse_access_contracts
from scion_sdk.connector import build_server
from scion_sdk.testing.surface_check import served_surface

ROW_ID = "CONN-CLARITY-API-CONNECTOR-CONTENT-R002"
CONTRACTS = (
    Path(__file__).resolve().parents[1]
    / "clarity_api"
    / "ontology"
    / "access_contracts.ttl"
)
RECORDINGS = Path(__file__).resolve().parent / "recordings"
EXPECTED = {
    "page_metric": {
        "class": "WebResource",
        "key": "url_date",
        "operation": "clarity_get_data_export",
        "columns": ("url", "date", "rageClickRate", "deadClickRate", "rageClickCount"),
    },
}


def _local(iri: str) -> str:
    return re.split(r"[#/]", iri)[-1]


def _declared_terms() -> set[str]:
    text = (CONTRACTS.parent / "clarity.ttl").read_text(encoding="utf-8")
    return set(re.findall(r"^:(\w+)\s+a\s+owl:", text, flags=re.M))


def _competency_findings(
    contracts, tools: set[str], terms: set[str], recordings: Path
) -> list[str]:
    found: list[str] = []
    by_entity = {c.entity: c for c in contracts}
    for entity, want in EXPECTED.items():
        contract = by_entity.get(entity)
        if contract is None:
            found.append(f"{entity}: no contract")
            continue
        if contract.operation not in tools:
            found.append(f"{entity}: tool {contract.operation} is not served")
        if _local(contract.class_iri) != want["class"] or (
            want["class"] not in terms and "/ontology/core#" not in contract.class_iri
        ):
            found.append(f"{entity}: class {contract.class_iri} not in ontology")
        if contract.key_field != want["key"] or contract.access_kind != "mcp_tool":
            found.append(f"{entity}: wrong key or access kind")
        bound = {field: prop for prop, field in contract.predicates}
        for field in want["columns"]:
            if (
                field not in bound
                or _local(bound[field]) != field
                or field not in terms
            ):
                found.append(f"{entity}: column {field} is not an ontology property")
        path = recordings / f"{entity}.json"
        if not path.is_file():
            found.append(f"{entity}: recording missing")
            continue
        records = json.loads(path.read_text(encoding="utf-8"))
        if not records:
            found.append(f"{entity}: recording is empty")
        for record in records:
            for field in {contract.key_field} | set(want["columns"]):
                if field not in record:
                    found.append(f"{entity}: recording lacks {field}")
    return found


def _contracts():
    return parse_access_contracts(CONTRACTS.read_text(encoding="utf-8"))


@pytest.mark.spec(ROW_ID)
def test_competency_contracts_certified() -> None:
    tools = served_surface(build_server("clarity_api", command_args=[])[1]).tools
    assert (
        _competency_findings(_contracts(), tools, _declared_terms(), RECORDINGS) == []
    )


@pytest.mark.spec(ROW_ID)
def test_missing_tool_or_column_fails_certification(tmp_path: Path) -> None:
    entity, want = next(iter(EXPECTED.items()))
    (tmp_path / f"{entity}.json").write_text(json.dumps([{want["key"]: "x"}]))
    found = _competency_findings(_contracts(), set(), _declared_terms(), tmp_path)
    assert any("is not served" in f for f in found)
    assert any("recording lacks" in f for f in found)
