"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` / ``map_export`` /
``ingest_export`` / ``ingest_response`` seam with a fake engine client (no engine
required), asserting the txn add_node/commit + edge calls and the Clarity export ->
:ClarityProject / :ClaritySession / :BehaviorInsight / :BehaviorDimension / :Document
mapping. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import json

import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError

from clarity_api.kg_ingest import (
    ingest_documents,
    ingest_entities,
    ingest_export,
    ingest_response,
    map_export,
)

_EXPORT = [
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


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def add_edge(self, txn, src, dst, props):
        self.edges.append((src, dst, props))

    def commit(self, txn):
        self.committed = True
        return True



class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()


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
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "clarity-api"
    assert c.txn.nodes["a"]["domain"] == "clarity"
    assert c.txn.edges == [("b", "a", {"relationship": "belongsToProject"})]


def test_ingest_documents_writes_document_nodes():
    c = _FakeClient()
    res = ingest_documents(
        [{"id": "clarity:doc:x", "text": "hello", "title": "T"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.txn.nodes["clarity:doc:x"]
    assert node["node_type"] == "Document"
    assert node["text"] == "hello"
    assert node["created_at"]  # stamped


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
    assert "clarity:project:acme" in c.txn.nodes
    assert "clarity:doc:acme:3:OS" in c.txn.nodes


def test_ingest_response_parses_data_envelope():
    c = _FakeClient()
    resp = _FakeResponse({"data": _EXPORT})
    res = ingest_response(
        resp, {"number_of_days": 3, "dimension_1": "os"}, project="acme", client=c
    )
    assert res is not None
    assert res["nodes"] > 0
    # canonicalized dimension "os" -> "OS"
    assert "clarity:dimension:OS" in c.txn.nodes


def test_ingest_response_parses_bare_list():
    c = _FakeClient()
    resp = _FakeResponse(json.loads(json.dumps(_EXPORT)))
    res = ingest_response(resp, {"numOfDays": 1}, project="acme", client=c)
    assert res is not None
    assert "clarity:project:acme" in c.txn.nodes


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
