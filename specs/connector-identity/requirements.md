# CONN-CLARITY-API-CONNECTOR-IDENTITY — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-CLARITY-API-CONNECTOR-IDENTITY-R001` | **Fleet name.** `pyproject.toml` declares `clarity-mcp` as the single `scion_sdk.connector` entry point. The content pack, the manifest `connector`, the fingerprints and the ingest binding all carry `clarity-mcp`. Proving test: `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name`. Caller chain: the scion_sdk.connector entry point clarity-mcp in pyproject.toml resolves to clarity_api/__init__.py::connector, and clarity_api/connector_sources.py::SOURCES declares server=clarity-mcp for the clarity_get_data_export source served via connector://resources. Shape: the entry point name, the server value in clarity_api/connector_sources.py, the IngestBinding in clarity_api/kg_ingest.py and scion_sdk.connector_identity.connector_name all carry clarity-mcp; tests/test_fleet_name.py scans these. | Every connector name in the package is `clarity-mcp`. |
