# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Standardized to the golden agent-package layout: MCP server (`clarity-mcp`),
  A2A agent server (`clarity-agent`), modular `api/` and `mcp/` sub-packages,
  `auth.py` dependency, docs site, Docker infrastructure, and CI workflows.
- Action-routed MCP tool `clarity_insights` (`CONCEPT:CLA-001`) for the
  Microsoft Clarity Data Export / Live Insights endpoint.

### Changed
- Migrated packaging from `setup.py` to a golden `pyproject.toml`.
- Mapped credentials to standardized env vars `CLARITY_URL`, `CLARITY_TOKEN`,
  and `CLARITY_SSL_VERIFY`.
- Refactored the `Api` client into a facade over the modular `api/` sub-package
  while preserving the original `Api`/`get_data_export` contract.

## [0.0.3]

### Added
- Initial release of the Microsoft Clarity Data Export API client.
