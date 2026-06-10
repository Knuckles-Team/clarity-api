# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Architecture overview, Table of Contents, and Environment Variables reference
  in the README.
- `@pytest.mark.concept("CLA-001")` markers and concept-tagged docstrings to
  trace the Data Export / Live Insights path (`CONCEPT:CLA-001`) across code,
  tests, and `docs/concepts.md`.
- Data-driven (`@pytest.mark.parametrize`) and negative/error-path tests
  (401/403/404 -> `AuthError`/`UnauthorizedError`/`ParameterError`).
- `clarity_api.services.InsightsService`: a thin, dependency-injected
  application-service seam between the MCP tool and the REST client.

### Changed
- The `clarity_insights` MCP tool now delegates to `InsightsService` rather
  than calling the client directly.

## [1.0.0] - 2026-06-10

### Added
- Standardized to the golden agent-package layout: MCP server (`clarity-mcp`),
  A2A agent server (`clarity-agent`), modular `api/` and `mcp/` sub-packages,
  `auth.py` dependency factory, docs site, Docker infrastructure, and CI
  workflows.
- Action-routed MCP tool `clarity_insights` (`CONCEPT:CLA-001`) for the
  Microsoft Clarity Data Export / Live Insights endpoint
  (`/export-data/api/v1/project-live-insights`).
- OIDC token-delegation (RFC 8693) and fixed-credential auth paths via the
  `get_client` dependency.
- Pydantic input/output models (`InputModel`, `Response`, `Metric`,
  `Information`) with dimension and date-range validation.

### Changed
- Migrated packaging from `setup.py` to a golden `pyproject.toml`.
- Mapped credentials to standardized env vars `CLARITY_URL`, `CLARITY_TOKEN`,
  and `CLARITY_SSL_VERIFY`.
- Refactored the `Api` client into a facade over the modular `api/` sub-package
  while preserving the original `Api`/`get_data_export` contract.

### Removed
- Legacy `setup.py` packaging in favor of `pyproject.toml`.

## [0.0.3] - 2024-01-01

### Added
- Initial release of the Microsoft Clarity Data Export API client.

[Unreleased]: https://github.com/Knuckles-Team/clarity-api/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Knuckles-Team/clarity-api/compare/v0.0.3...v1.0.0
[0.0.3]: https://github.com/Knuckles-Team/clarity-api/releases/tag/v0.0.3
