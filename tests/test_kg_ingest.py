"""Knowledge-graph ingestion coverage for the Microsoft Clarity connector.

Exercises the real ``ingest_entities`` / ``ingest_documents`` / ``map_export`` /
``ingest_export`` / ``ingest_response`` seam against a fake
``agent_connector_sdk.ingest`` transport (no engine required), asserting the
submitted records/relationships and the Clarity export ->
:ClarityProject / :ClaritySession / :BehaviorInsight / :BehaviorDimension / :Document
mapping. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest

from clarity_api.kg_ingest import (
    ingest_documents,
    ingest_entities,
    ingest_export,
    ingest_response,
    map_export,
)

_EXPORT: list[dict[str, Any]] = [
    {
        "metricName": "Traffic",
        "information": [
            {
                "totalSessionCount": "100",
                "totalBotSessionCount": "10",
                "distantUserCount": "90",
                "PagesPerSessionPercentage": 1.5,
                "OS": "Android",
            },
            {
                "totalSessionCount": "40",
                "totalBotSessionCount": "5",
                "distantUserCount": "35",
                "OS": "iOS",
            },
        ],
    },
    {
        "metricName": "EngagementTime",
        "information": [{"totalTime": "1234", "OS": "Android"}],
    },
]


class _FakeTransport:
    """Fakes the transport boundary one level below ``KnowledgeIngest``."""

    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def source_status(self, connector: str, stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: Any) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
        )

    async def store_blob(self, data: bytes) -> str:
        raise AssertionError("this connector's ingestion carries no media")


@pytest.fixture
def ingest() -> tuple[KnowledgeIngest, _FakeTransport]:
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


class _FakeResponse:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def json(self) -> Any:
        return self._payload


async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "ClarityProject", "name": "p"},
            {"id": "b", "node_type": "ClaritySession"},
        ],
        [{"source": "b", "target": "a", "relationship": "belongsToProject"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(transport.requests) == 1
    request = transport.requests[0]
    ids = {record.record_id for record in request.records}
    assert ids == {"a", "b"}
    assert request.relationships[0].relation_reference.endswith(
        "/belongsToProject"
    )


async def test_ingest_documents_writes_document_nodes(ingest):
    service, transport = ingest
    res = await ingest_documents(
        [{"id": "clarity:doc:x", "text": "hello", "title": "T"}],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    request = transport.requests[0]
    assert len(request.records) == 1


def test_map_export_builds_typed_nodes_and_links():
    entities, relationships, documents = map_export(
        _EXPORT, project="acme", num_of_days=3, dimensions=["OS"]
    )
    by_id = {e["id"]: e for e in entities}

    # project
    assert by_id["clarity:project:acme"]["node_type"] == "ClarityProject"
    # session snapshot aggregates counts across the first count-bearing metric
    sess = by_id["clarity:session:acme:3:OS"]
    assert sess["node_type"] == "ClaritySession"
    assert sess["totalSessionCount"] == 140
    assert sess["totalBotSessionCount"] == 15
    assert sess["distinctUserCount"] == 125
    assert sess["pagesPerSessionPercentage"] == 1.5
    # one insight per metric
    assert by_id["clarity:insight:acme:3:OS:Traffic"]["metricName"] == "Traffic"
    assert (
        by_id["clarity:insight:acme:3:OS:EngagementTime"]["node_type"]
        == "BehaviorInsight"
    )
    # dimension node
    assert by_id["clarity:dimension:OS"]["dimensionName"] == "OS"
    # document summary
    assert documents[0]["id"] == "clarity:doc:acme:3:OS"
    assert "acme" in documents[0]["text"]

    rel_types = {r["relationship"] for r in relationships}
    assert {
        "belongsToProject",
        "hasInsight",
        "brokenDownBy",
        "summarizedBy",
    } <= rel_types


async def test_ingest_export_writes_nodes_and_documents(ingest):
    service, transport = ingest
    res = await ingest_export(
        _EXPORT, project="acme", num_of_days=3, dimensions=["OS"], ingest=service
    )
    assert res is not None
    assert res["nodes"] > 0
    assert res["documents"] == 1
    # one submit for entities+relationships, one for documents
    assert len(transport.requests) == 2


async def test_ingest_response_parses_data_envelope(ingest):
    service, _transport = ingest
    resp = _FakeResponse({"data": _EXPORT})
    res = await ingest_response(
        resp, {"number_of_days": 3, "dimension_1": "os"}, project="acme", ingest=service
    )
    assert res is not None
    assert res["nodes"] > 0


async def test_ingest_response_parses_bare_list(ingest):
    service, _transport = ingest
    resp = _FakeResponse(json.loads(json.dumps(_EXPORT)))
    res = await ingest_response(resp, {"numOfDays": 1}, project="acme", ingest=service)
    assert res is not None
    assert res["nodes"] > 0


async def test_ingest_response_materializes_empty_snapshot(ingest):
    service, _transport = ingest
    first = await ingest_response(_FakeResponse({"data": []}), {}, ingest=service)
    second = await ingest_response(_FakeResponse("nonsense"), {}, ingest=service)
    assert first == {"nodes": 2, "edges": 2, "documents": 1}
    assert second == first


async def test_ingest_empty_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)
