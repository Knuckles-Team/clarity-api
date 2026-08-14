"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` / ``map_export`` /
``ingest_export`` / ``ingest_response`` seam with a fake engine client (no engine
required), asserting the txn add_node/commit + edge calls and the Clarity export ->
:ClarityProject / :ClaritySession / :BehaviorInsight / :BehaviorDimension / :Document
mapping. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import json
from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.security.brain_context import ActorContext, use_actor
from agent_utilities.models.company_brain import ActorType
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session

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


@pytest.fixture(autouse=True)
def _governed_session():
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "ClarityProject", "name": "p"},
            {"id": "b", "node_type": "ClaritySession"},
        ],
        [{"source": "b", "target": "a", "relationship": "belongsToProject"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) == 1
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "clarity-api"
    assert c.nodes.values["a"]["domain"] == "clarity"
    assert c.changes.edges == [("b", "a", {"relationship": "belongsToProject"})]


def test_ingest_documents_writes_document_nodes():
    c = _FakeClient()
    res = ingest_documents(
        [{"id": "clarity:doc:x", "text": "hello", "title": "T"}],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.nodes.values["clarity:doc:x"]
    assert node["node_type"] == "Document"
    assert node["text"] == "hello"
    assert node["needs_enrichment"] is True  # stamped


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
        by_id["clarity:insight:acme:3:OS:EngagementTime"]["node_type"] == "BehaviorInsight"
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


def test_ingest_export_writes_nodes_and_documents():
    c = _FakeClient()
    res = ingest_export(
        _EXPORT, project="acme", num_of_days=3, dimensions=["OS"], client=c
    )
    assert res is not None
    assert res["nodes"] > 0
    assert res["documents"] == 1
    assert "clarity:project:acme" in c.nodes.values
    assert "clarity:doc:acme:3:OS" in c.nodes.values


def test_ingest_response_parses_data_envelope():
    c = _FakeClient()
    resp = _FakeResponse({"data": _EXPORT})
    res = ingest_response(
        resp, {"number_of_days": 3, "dimension_1": "os"}, project="acme", client=c
    )
    assert res is not None
    assert res["nodes"] > 0
    # canonicalized dimension "os" -> "OS"
    assert "clarity:dimension:OS" in c.nodes.values


def test_ingest_response_parses_bare_list():
    c = _FakeClient()
    resp = _FakeResponse(json.loads(json.dumps(_EXPORT)))
    res = ingest_response(resp, {"numOfDays": 1}, project="acme", client=c)
    assert res is not None
    assert "clarity:project:acme" in c.nodes.values


def test_ingest_response_materializes_empty_snapshot():
    first = ingest_response(_FakeResponse({"data": []}), {}, client=_FakeClient())
    second = ingest_response(_FakeResponse("nonsense"), {}, client=_FakeClient())
    assert first == {"nodes": 2, "edges": 2, "documents": 1}
    assert second == first


def test_ingest_rejects_legacy_structural_fields():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "legacy", "type": "Legacy"}], client=_FakeClient())


def test_ingest_empty_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
