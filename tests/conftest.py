import json
from unittest.mock import patch

import pytest
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session
from agent_utilities.models.company_brain import ActorType
from agent_utilities.security.brain_context import ActorContext, use_actor
from dotenv import load_dotenv

# Use a reason variable for skipped tests
reason = "Unit tests using mocks"


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("CLARITY_URL", "https://test.clarity.ms")
    monkeypatch.setenv("CLARITY_TOKEN", "mock_token")


@pytest.fixture(autouse=True)
def _governed_session():
    """Ambient GraphSession for native_ingest calls (mirrors agent-utilities'
    own tests/knowledge_graph/test_native_ingest.py::_governed_session) — every
    graph write now requires a verified ambient session (AU-P0-1)."""
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


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(autouse=True)
def mock_requests():
    """Mock all outbound HTTP so the Api validation + data export succeed offline."""

    def mock_side_effect(*args, **kwargs):
        from requests import Response

        mock_response = Response()
        mock_response.status_code = 200
        url = kwargs.get("url", "") or (args[0] if args else "")

        if url.endswith("/projects"):
            data: list | dict = [{"id": 1, "name": "test"}]
        elif "project-live-insights" in url:
            data = {
                "data": [
                    {
                        "metricName": "Traffic",
                        "information": [
                            {
                                "totalSessionCount": "100",
                                "totalBotSessionCount": "10",
                                "distantUserCount": "90",
                                "PagesPerSessionPercentage": 1.5,
                                "OS": "Android",
                            }
                        ],
                    }
                ]
            }
        else:
            data = kwargs.get("json", {}) or {"id": 1, "name": "test"}

        mock_response._content = json.dumps(data).encode("utf-8")
        return mock_response

    with (
        patch("requests.Session.get", side_effect=mock_side_effect) as mock_get,
        patch("requests.Session.post", side_effect=mock_side_effect) as mock_post,
        patch("requests.Session.request", side_effect=mock_side_effect) as mock_req,
    ):
        yield {"get": mock_get, "post": mock_post, "request": mock_req}
