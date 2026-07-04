"""Native epistemic-graph ingestion for Microsoft Clarity records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The clarity-api connector natively
pushes its behavioral-analytics data into the ONE epistemic-graph knowledge graph as
**typed OWL nodes** (``:ClarityProject``, ``:ClaritySession``, ``:BehaviorInsight``,
``:BehaviorDimension``) + ``:Document`` summaries and links, using the lightweight engine
client (``GraphComputeEngine()._client`` + ``txn``) — the same fast client the blob
``MediaStore`` uses, NOT the heavy in-process ingestion engine.

This is a thin mapper over the shared primitive
``agent_utilities.knowledge_graph.memory.native_ingest``; when that primitive is not
present in the installed ``agent_utilities`` it falls back to a self-contained txn write
path with identical behavior. Everything is dependency-/engine-guarded: with no KG stack
or no reachable engine every entry point **no-ops** (returns ``None``), so the connector
keeps working with zero KG infrastructure. Nodes carry the shared provenance
(``domain``/``source``) and match the classes federated by ``clarity_api.ontology``.
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger("clarity_api.kg")

_SOURCE = "clarity-api"
_DOMAIN = "clarity"
_DEFAULT_GRAPH = "__commons__"

# Canonical dimension names Clarity segments metrics by (mirrors InputModel).
_DIMENSIONS = (
    "Browser",
    "Device",
    "Country",
    "OS",
    "Source",
    "Medium",
    "Campaign",
    "Channel",
    "URL",
)


def _native() -> Any | None:
    """Return the shared ``native_ingest`` module, or ``None`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.memory import (  # type: ignore
            native_ingest,
        )
    except Exception as e:  # noqa: BLE001 — primitive not yet installed
        logger.debug("native_ingest primitive unavailable: %s", e)
        return None
    return native_ingest


def _client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    native = _native()
    if native is not None:
        return native.native_client()
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        return client, (getattr(engine, "graph_name", None) or _DEFAULT_GRAPH)
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def _write_nodes(
    client: Any,
    graph: str,
    nodes: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None,
    *,
    source: str,
    domain: str,
) -> dict[str, int] | None:
    """Self-contained txn fallback: stamp provenance, MERGE nodes, add edges."""
    nodes = [n for n in nodes if n.get("id")]
    if not nodes:
        return None
    try:
        txn = client.txn.begin(graph=graph)
        for node in nodes:
            props = {k: v for k, v in node.items() if k != "id" and v is not None}
            props.setdefault("source", source)
            props.setdefault("domain", domain)
            client.txn.add_node(txn, node["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None

    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)

    logger.info("KG ingest[%s]: wrote %d nodes, %d edges", domain, len(nodes), edges)
    return {"nodes": len(nodes), "edges": edges}


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed OWL nodes (+ edges) into epistemic-graph via the fast engine client.

    ``entities``: ``[{"id":..., "type":<owl:Class>, ...props}]``.
    ``relationships``: ``[{"source":id, "target":id, "type":rel}]``.
    Returns ``{"nodes":n, "edges":m}`` or ``None`` (no engine / failure; never raises).
    ``client``/``graph`` may be injected (tests); otherwise resolved on demand.
    """
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None
    native = _native()
    if native is not None:
        return native.ingest_entities(
            entities,
            relationships,
            source=source,
            domain=domain,
            client=client,
            graph=graph,
        )
    if client is None:
        client, graph = _client()
    if client is None:
        return None
    return _write_nodes(
        client,
        graph or _DEFAULT_GRAPH,
        entities,
        relationships,
        source=source,
        domain=domain,
    )


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    Returns ``{"nodes":n, "edges":0}`` or ``None``.
    """
    native = _native()
    if native is not None:
        return native.ingest_documents(
            documents, source=source, domain=domain, client=client, graph=graph
        )
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    nodes: list[dict[str, Any]] = []
    for doc in documents or []:
        did = doc.get("id")
        text = doc.get("text") or doc.get("content")
        if not did or not text:
            continue
        node = {k: v for k, v in doc.items() if k not in ("content",) and v is not None}
        node["id"] = did
        node["type"] = "Document"
        node["text"] = text
        node.setdefault("created_at", now)
        nodes.append(node)
    if not nodes:
        return None
    if client is None:
        client, graph = _client()
    if client is None:
        return None
    return _write_nodes(
        client, graph or _DEFAULT_GRAPH, nodes, None, source=source, domain=domain
    )


# --- Clarity record -> typed-node mapping ----------------------------------


def _dim_key(dimensions: list[str]) -> str:
    return "-".join(d for d in dimensions if d) or "overall"


def _as_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def map_export(
    metrics: list[dict[str, Any]],
    *,
    project: str = "default",
    num_of_days: int | None = None,
    dimensions: list[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Map a Clarity Data Export payload to ``(entities, relationships, documents)``.

    ``metrics`` is the ``data`` list of the ``project-live-insights`` response —
    ``[{"metricName":..., "information":[{...rows}]}]``. Produces a ``:ClarityProject``,
    one ``:ClaritySession`` snapshot (aggregated session counts), a ``:BehaviorInsight``
    per metric, ``:BehaviorDimension`` nodes for the breakdown, and a ``:Document``
    summary — with ``:belongsToProject`` / ``:hasInsight`` / ``:brokenDownBy`` /
    ``:summarizedBy`` links.
    """
    dimensions = [d for d in (dimensions or []) if d]
    dimkey = _dim_key(dimensions)
    days = num_of_days if num_of_days is not None else 0
    pid = f"clarity:project:{project}"
    sid = f"clarity:session:{project}:{days}:{dimkey}"
    docid = f"clarity:doc:{project}:{days}:{dimkey}"

    entities: list[dict[str, Any]] = [
        {
            "id": pid,
            "type": "ClarityProject",
            "name": project,
            "externalToolId": project,
        }
    ]
    relationships: list[dict[str, Any]] = []

    # Aggregate the session-count snapshot from the first metric carrying counts.
    total_sessions = 0
    total_bots = 0
    distinct_users = 0
    pages_per_session: float | None = None
    for metric in metrics or []:
        rows = metric.get("information") or []
        counted = False
        for row in rows:
            ts = _as_int(row.get("totalSessionCount"))
            if ts is None:
                continue
            counted = True
            total_sessions += ts
            total_bots += _as_int(row.get("totalBotSessionCount")) or 0
            distinct_users += _as_int(row.get("distantUserCount")) or 0
            if pages_per_session is None:
                pages_per_session = _as_float(row.get("PagesPerSessionPercentage"))
        if counted:
            break

    session_node = {
        "id": sid,
        "type": "ClaritySession",
        "name": f"{project} — {days}d / {dimkey}",
        "numOfDays": days,
        "externalToolId": f"{project}:{days}:{dimkey}",
        "totalSessionCount": total_sessions,
        "totalBotSessionCount": total_bots,
        "distinctUserCount": distinct_users,
    }
    if pages_per_session is not None:
        session_node["pagesPerSessionPercentage"] = pages_per_session
    entities.append(session_node)
    relationships.append({"source": sid, "target": pid, "type": "belongsToProject"})

    # Dimension nodes (shared across insights).
    for dim in dimensions:
        did = f"clarity:dimension:{dim}"
        entities.append(
            {"id": did, "type": "BehaviorDimension", "dimensionName": dim, "name": dim}
        )

    # One BehaviorInsight per metric.
    for metric in metrics or []:
        mname = metric.get("metricName")
        if not mname:
            continue
        iid = f"clarity:insight:{project}:{days}:{dimkey}:{mname}"
        rows = metric.get("information") or []
        entities.append(
            {
                "id": iid,
                "type": "BehaviorInsight",
                "metricName": mname,
                "name": f"{mname} ({days}d / {dimkey})",
                "numOfDays": days,
                "rowCount": len(rows),
                "externalToolId": f"{project}:{days}:{dimkey}:{mname}",
            }
        )
        relationships.append({"source": iid, "target": pid, "type": "belongsToProject"})
        relationships.append({"source": sid, "target": iid, "type": "hasInsight"})
        for dim in dimensions:
            relationships.append(
                {
                    "source": iid,
                    "target": f"clarity:dimension:{dim}",
                    "type": "brokenDownBy",
                }
            )

    # Document summary for semantic search.
    metric_names = [m.get("metricName") for m in metrics or [] if m.get("metricName")]
    summary = (
        f"Microsoft Clarity export for project '{project}' over {days} day(s), "
        f"broken down by {dimkey}. Metrics: {', '.join(metric_names) or 'none'}. "
        f"Aggregate sessions: {total_sessions} "
        f"(bots: {total_bots}, distinct users: {distinct_users})."
    )
    documents = [
        {
            "id": docid,
            "title": f"Clarity export — {project} ({days}d / {dimkey})",
            "text": summary,
            "source_uri": f"clarity://{project}/{days}/{dimkey}",
        }
    ]
    relationships.append({"source": sid, "target": docid, "type": "summarizedBy"})

    return entities, relationships, documents


_DIM_CANONICAL = {
    "browser": "Browser",
    "device": "Device",
    "country": "Country",
    "os": "OS",
    "source": "Source",
    "medium": "Medium",
    "campaign": "Campaign",
    "channel": "Channel",
    "url": "URL",
}


def _project_label(project: str | None = None) -> str:
    """Derive a stable project label from the Clarity host, or use ``project``."""
    if project:
        return project
    try:
        from urllib.parse import urlparse

        from agent_utilities.core.config import setting

        host = urlparse(setting("CLARITY_URL", "https://www.clarity.ms")).netloc
        return host or "default"
    except Exception:  # noqa: BLE001
        return "default"


def _dims_from_params(params: dict[str, Any]) -> list[str]:
    """Pull the up-to-three dimension values out of a params dict, canonicalized."""
    dims: list[str] = []
    for a, b in (
        ("dimension1", "dimension_1"),
        ("dimension2", "dimension_2"),
        ("dimension3", "dimension_3"),
    ):
        raw = params.get(a) or params.get(b)
        if raw:
            dims.append(_DIM_CANONICAL.get(str(raw).lower(), str(raw)))
    return dims


def ingest_response(
    response: Any,
    params: dict[str, Any] | None = None,
    *,
    project: str | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Best-effort fetch-flow hook: ingest a Clarity ``requests.Response``.

    Extracts the metrics list from the export payload (a bare list, or a dict with a
    ``data`` list) and pushes typed nodes + a summary document. Never raises; returns
    ``None`` when the payload has no metrics or no engine is reachable.
    """
    params = params or {}
    try:
        payload = response.json()
    except Exception:  # noqa: BLE001 — non-JSON / error responses are skipped
        return None
    if isinstance(payload, list):
        metrics = payload
    elif isinstance(payload, dict):
        metrics = payload.get("data")
    else:
        metrics = None
    if not isinstance(metrics, list) or not metrics:
        return None
    num_of_days = _as_int(params.get("number_of_days") or params.get("numOfDays"))
    return ingest_export(
        metrics,
        project=_project_label(project),
        num_of_days=num_of_days,
        dimensions=_dims_from_params(params),
        client=client,
        graph=graph,
    )


def ingest_export(
    metrics: list[dict[str, Any]],
    *,
    project: str = "default",
    num_of_days: int | None = None,
    dimensions: list[str] | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map a Clarity export payload and ingest its nodes, links, and summary document.

    Returns a merged ``{"nodes":n, "edges":m, "documents":d}`` or ``None`` when nothing
    was written (no engine / empty payload).
    """
    entities, relationships, documents = map_export(
        metrics, project=project, num_of_days=num_of_days, dimensions=dimensions
    )
    ent_res = ingest_entities(entities, relationships, client=client, graph=graph)
    doc_res = ingest_documents(documents, client=client, graph=graph)
    if ent_res is None and doc_res is None:
        return None
    return {
        "nodes": (ent_res or {}).get("nodes", 0),
        "edges": (ent_res or {}).get("edges", 0),
        "documents": (doc_res or {}).get("nodes", 0),
    }
