---
name: clarity-api-development
skill_type: skill
description: >-
  Develop, test, and publish the clarity-api connector without breaking its
  typed Clarity export contract, packaged content, spec delivery dashboard, or
  governed Pages workflow. Use when changing connector code, docs, skills,
  workflows, or repository-owned specs.
license: MIT
tags: [clarity, connector, development, testing, pages, specs]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# Clarity API Development

Use this skill for changes inside the clarity-api package. The connector wraps
Microsoft Clarity's live-insights export behind a typed client, MCP tool, A2A
agent, and packaged skill/content resources. Keep those surfaces aligned when a
change crosses a boundary.

## Repository map

- clarity_api/api/ contains the composable HTTP client mixins and Api facade.
- clarity_api/mcp/ registers action-routed tools over an injected client.
- clarity_api/services/ owns the export use case and its knowledge-graph
  ingestion seam.
- clarity_api/skills/, prompts/, ontology/, and connectors/ are packaged
  resources exposed by the connector entry point.
- specs/connector-content/ and specs/connector-identity/ are the source
  specifications; their status.json files are generated evidence, never hand
  edited.

## Before editing

1. Work from a real worktree based on the repository's current origin/main.
2. Find the owning row under specs/ before adding behavior, and preserve the
   existing CONCEPT: registry when a domain capability is involved.
3. Trace a changed input from the MCP model through the service and API client
   to the response model. Do not add a second route for the same export call.
4. Keep credentials and external Clarity calls out of tests; use the existing
   request fixtures and mock clients.

## Implementation contract

- Preserve the clarity-mcp connector name and the public Api /
  get_data_export contract.
- Validate request bounds and dimensions at the Pydantic boundary. Keep response
  envelopes and redaction behavior consistent with neighboring tools.
- Use the shared agent-utilities server/agent factories and the injected
  client seam. Do not import runtime code from another connector.
- Add or update a focused test when behavior changes. Test refusal and malformed
  input paths as well as the successful response shape.
- Keep all package resources under the existing package-data globs so an sdist
  and wheel expose the same skills, prompts, ontology, and connector manifest.

## Rapid delivery: the 5-minute contract

Specs are already designed. Deliver one small, reviewable change at a time.

- Start with one owning requirement and state its proof before editing.
- Keep a slice to one connector concern: source code, one test seam, one
  workflow/configuration repair, or one substantive skill.
- Run the smallest relevant tests first, then the repository pre-commit suite
  on the candidate worktree. Fix warnings and failures rather than bypassing a
  hook.
- Record the exact source and test commands in the commit or review handoff.
- Never claim a Pages or spec row from a YAML marker alone: the dashboard config,
  generated status records, successful exact-source workflow, and published
  page must agree.
- Commit only reviewed paths with an explicit path list. Never stage a whole
  shared checkout, credentials, caches, generated logs, or temporary output.

## Spec delivery and Pages

The canonical Pages caller is .github/workflows/pages.yml. This repository uses
the docs/ content source, so the caller must pass content_source: docs, enable
spec_dashboard_enabled, and point spec_dashboard_config at
.github/spec-dashboard.json. The push path set must include specs/**, the
dashboard config, and the Pages workflow itself in addition to documentation
paths. Keep the config versioned and bounded to specs/*/status.json; the
central renderer owns the HTML layout.

Regenerate status evidence with the pipeline hook when a spec changes, inspect
the resulting diff, and verify that no status row was advanced without a real
implementation or test receipt. The Pages proof is complete only after the
published run uses the candidate commit and /spec-delivery/ serves the
candidate snapshot.

## Verification

From the repository root:

    pre-commit run --all-files
    python -m pytest tests -q

Prefer focused tests for the touched module while iterating. For Pages changes,
also run the central dashboard renderer against a task-local output directory
and verify the config parses, status files are discovered, and the result
contains the connector content and identity records.

## Safety

Never commit .env files, tokens, raw Clarity identifiers, or generated site
output. Never make live Clarity calls from tests. Preserve the destructive
boundary and the no-engine ingestion no-op semantics. If a dependency or
packaged metadata change is necessary, update the lockfile in the same slice
and explain why in the review.
