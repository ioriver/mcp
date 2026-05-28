"""
Integration tests for the FastAPI auth middleware and health endpoint.

Uses httpx.AsyncClient with ASGITransport to send real HTTP requests
through the app without starting a server. The IoRiver API is never called
since tools are not invoked in these tests.
"""

from unittest.mock import patch

from httpx import AsyncClient, ASGITransport

# main is imported after conftest has patched sys.path
from main import app, mcp


async def _fake_mcp_handle(_scope, _receive, send):
    """Minimal ASGI response used to replace the real MCP session manager."""
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", b"2"),
        ],
    })
    await send({"type": "http.response.body", "body": b"{}", "more_body": False})


class TestHealthEndpoint:
    async def test_health_returns_200(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_returns_ok(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.json() == {"status": "ok"}

    async def test_health_requires_no_auth(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.status_code != 401


class TestAuthMiddleware:
    """Tests for the Bearer token enforcement on /mcp paths."""

    MCP_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    MCP_BODY = {"jsonrpc": "2.0", "method": "tools/list", "id": 1}

    async def test_missing_auth_header_returns_401(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/mcp",
                json=self.MCP_BODY,
                headers=self.MCP_HEADERS,
            )
        assert response.status_code == 401

    async def test_non_bearer_scheme_returns_401(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/mcp",
                json=self.MCP_BODY,
                headers={**self.MCP_HEADERS, "Authorization": "Token mytoken"},
            )
        assert response.status_code == 401

    async def test_basic_auth_returns_401(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/mcp",
                json=self.MCP_BODY,
                headers={**self.MCP_HEADERS, "Authorization": "Basic dXNlcjpwYXNz"},
            )
        assert response.status_code == 401

    async def test_401_body_contains_error_message(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/mcp", json=self.MCP_BODY)
        data = response.json()
        assert "error" in data
        assert "Bearer" in data["error"]

    async def test_valid_bearer_token_passes_middleware(self):
        with patch.object(mcp.session_manager, "handle_request", side_effect=_fake_mcp_handle):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/mcp",
                    json=self.MCP_BODY,
                    headers={**self.MCP_HEADERS, "Authorization": "Bearer mytoken"},
                )
        assert response.status_code != 401

    async def test_bearer_case_insensitive(self):
        with patch.object(mcp.session_manager, "handle_request", side_effect=_fake_mcp_handle):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/mcp",
                    json=self.MCP_BODY,
                    headers={**self.MCP_HEADERS, "Authorization": "BEARER mytoken"},
                )
        assert response.status_code != 401

    async def test_non_mcp_path_requires_no_auth(self):
        """Paths other than /mcp should not be gated by the middleware."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.status_code != 401
