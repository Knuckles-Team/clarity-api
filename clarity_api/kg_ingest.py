"""Native epistemic-graph ingestion for Microsoft Clarity records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The clarity-api connector natively
pushes its behavioral-analytics data into the ONE epistemic-graph knowledge graph as
**typed OWL nodes** (``:ClarityProject``, ``:ClaritySession``, ``:BehaviorInsight``,
``:BehaviorDimension``) + ``:Document`` summaries and links through the required
``agent_utilities.knowledge_graph.memory.native_ingest`` authority. Nodes carry shared
provenance (``domain``/``source``) and match the classes federated by
``clarity_api.ontology``.
"""

from __future__ import annotations

from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_documents as _native_ingest_documents,
)
from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)

_SOURCE = "clarity-api"
_DOMAIN = "clarity"

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


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write canonical typed nodes and relationships through native ingestion."""
    return _native_ingest_entities(
        entities,
        relationships,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
    )


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    Validation and engine failures are surfaced as ``NativeIngestError``.
    """
    return _native_ingest_documents(
        documents, source=source, domain=domain, client=client, graph=graph
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
            "node_type": "ClarityProject",
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
        "node_type": "ClaritySession",
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
    relationships.append(
        {"source": sid, "target": pid, "relationship": "belongsToProject"}
    )

    # Dimension nodes (shared across insights).
    for dim in dimensions:
        did = f"clarity:dimension:{dim}"
        entities.append(
            {
                "id": did,
                "node_type": "BehaviorDimension",
                "dimensionName": dim,
                "name": dim,
            }
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
                "node_type": "BehaviorInsight",
                "metricName": mname,
                "name": f"{mname} ({days}d / {dimkey})",
                "numOfDays": days,
                "rowCount": len(rows),
                "externalToolId": f"{project}:{days}:{dimkey}:{mname}",
            }
        )
        relationships.append(
            {"source": iid, "target": pid, "relationship": "belongsToProject"}
        )
        relationships.append(
            {"source": sid, "target": iid, "relationship": "hasInsight"}
        )
        for dim in dimensions:
            relationships.append(
                {
                    "source": iid,
                    "target": f"clarity:dimension:{dim}",
                    "relationship": "brokenDownBy",
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
    relationships.append(
        {"source": sid, "target": docid, "relationship": "summarizedBy"}
    )

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
) -> dict[str, int]:
    """Ingest a Clarity ``requests.Response`` through the native authority.

    Extracts the metrics list from the export payload (a bare list, or a dict with a
    ``data`` list) and pushes typed nodes plus a summary document. Parse, validation,
    and native-ingestion failures propagate.
    """
    params = params or {}
    payload = response.json()
    if isinstance(payload, list):
        metrics = payload
    elif isinstance(payload, dict):
        metrics = payload.get("data")
    else:
        metrics = None
    if not isinstance(metrics, list):
        metrics = []
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
) -> dict[str, int]:
    """Map a Clarity export payload and ingest its nodes, links, and summary document.

    Returns merged node, edge, and document counts. Native failures propagate.
    """
    entities, relationships, documents = map_export(
        metrics, project=project, num_of_days=num_of_days, dimensions=dimensions
    )
    ent_res = ingest_entities(entities, relationships, client=client, graph=graph)
    doc_res = ingest_documents(documents, client=client, graph=graph)
    return {
        "nodes": ent_res.get("nodes", 0),
        "edges": ent_res.get("edges", 0),
        "documents": doc_res.get("nodes", 0),
    }
