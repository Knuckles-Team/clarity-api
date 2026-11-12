"""Surface contracts: tool use, links, data locations and business roles."""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

_DENIED = Refusal(
    "ACCESS_DENIED", "the token is missing, expired or scoped to another project"
)
_BAD_ARGUMENT = Refusal(
    "INVALID_ARGUMENT",
    "number_of_days is not 1, 2 or 3, or a dimension name is not supported",
)

CONTRACTS = (
    ToolUseContract(
        "report-behavior-by-dimension",
        (
            ToolStep(
                "clarity_get_data_export",
                params=("number_of_days", "dimension_1", "dimension_2", "dimension_3"),
                result=("metricName", "information"),
                refusals=(_DENIED, _BAD_ARGUMENT),
            ),
        ),
        "Read live insights for a window and break them down by up to three dimensions.",
    ),
    ToolUseContract(
        "capture-insights-to-graph",
        (
            ToolStep(
                "clarity_get_data_export",
                params=("number_of_days", "dimension_1", "dimension_2", "dimension_3"),
                result=("metricName", "information"),
                refusals=(_DENIED, _BAD_ARGUMENT),
            ),
            ToolStep(
                "clarity_ingest_insights",
                params=("number_of_days", "dimension_1", "dimension_2", "dimension_3"),
                result=("ingested",),
                refusals=(
                    _DENIED,
                    _BAD_ARGUMENT,
                    Refusal(
                        "NO_ENGINE",
                        "no knowledge-graph engine is reachable, so ingested is null",
                    ),
                ),
            ),
        ),
        "Read an export and write it to the knowledge graph as typed nodes and a summary document.",
    ),
)

LINKS = (
    SurfaceLink(
        "report-behavior-by-dimension",
        tools=("clarity_get_data_export",),
        prompts=("clarity-operator", "clarity-behavior-analyst"),
        skills=("clarity-behavioral-insights",),
    ),
    SurfaceLink(
        "capture-insights-to-graph",
        tools=("clarity_get_data_export", "clarity_ingest_insights"),
        prompts=(
            "clarity-operator",
            "clarity-behavior-analyst",
            "clarity-data-steward",
        ),
        skills=("clarity-analytics-ingestion",),
    ),
    SurfaceLink(
        "clarity-api-operations",
        tools=("clarity_get_data_export", "clarity_ingest_insights"),
        skills=("clarity-api-operations",),
    ),
)

LOCATIONS = (
    DataLocation(
        "clarity-live-insights",
        ("ClarityProject", "ClaritySession", "BehaviorInsight", "BehaviorDimension"),
        "CLARITY_URL",
        "clarity_get_data_export",
    ),
)

ROLES = (
    BusinessRole(
        "behavior-analyst",
        tasks=("report-behavior-by-dimension", "capture-insights-to-graph"),
    ),
    BusinessRole("data-steward", tasks=("capture-insights-to-graph",)),
)
