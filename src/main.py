"""
IO River MCP Server
-------------------
Uses FastMCP (stateless_http=True) mounted into FastAPI.

Token flow (same as Cloudflare's MCP server):
  Claude Desktop → mcp-remote → Bearer <token> → this server → Token <token> → api.ioriver.io

The Bearer token is extracted from each incoming request via middleware
and stored in a context variable so tools can access it per-request.
"""

import logging
import contextlib
import os
import sys
from contextvars import ContextVar
import uvicorn
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from settings import MCP_CONFIG_PORT
from tools.traffic_policies import register_traffic_policy_tools
from tools.traffic_analytics import register_traffic_analytics_tools
from tools.services import register_service_tools
from tools.security_analytics import register_security_analytics_tools
from tools.purge import register_purge_tools
from tools.monitors import register_monitor_tools
from tools.events import register_event_tools
from tools.certificates import register_certificate_tools
from tools.behaviors import register_behavior_tools
from tools.traffic_stats import register_traffic_stats_tools
from tools.alerts import register_alert_tools
from tools.account_providers import register_account_provider_tools
from ioriver import IoRiverClient

sys.path.insert(0, os.path.dirname(__file__))


# Context variable that holds the Bearer token for the current request.
# This is how we pass the per-request token into tool handlers safely
# without any global state.
_token_var: ContextVar[str] = ContextVar("ioriver_token")


def get_client() -> IoRiverClient:
    """Returns an IO River client scoped to the current request's token."""
    return IoRiverClient(_token_var.get())


# ---------------------------------------------------------------------------
# FastMCP server — stateless, one global instance, tools use _token_var
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "ioriver-mcp",
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

register_account_provider_tools(mcp, get_client)
register_service_tools(mcp, get_client)
register_monitor_tools(mcp, get_client)
register_purge_tools(mcp, get_client)
register_certificate_tools(mcp, get_client)
register_alert_tools(mcp, get_client)
register_security_analytics_tools(mcp, get_client)
register_traffic_stats_tools(mcp, get_client)
register_behavior_tools(mcp, get_client)
register_event_tools(mcp, get_client)
register_traffic_policy_tools(mcp, get_client)
register_traffic_analytics_tools(mcp, get_client)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="IO River MCP Server", lifespan=lifespan)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """
    Validates the Bearer token on all /mcp requests and stores it
    in the context variable so tool handlers can use it.
    """
    if request.method == "OPTIONS":
        response = Response(status_code=204)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    if request.url.path.startswith("/mcp"):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": (
                        "Missing or invalid Authorization header. "
                        "Use: Authorization: Bearer <your-ioriver-api-token>"
                    )
                },
            )
        token_ctx = _token_var.set(auth_header)
        try:
            response = await call_next(request)
        finally:
            _token_var.reset(token_ctx)
        return response

    return await call_next(request)


@app.get("/health")
async def health():
    """K8s liveness and readiness probe."""
    return {"status": "ok"}


# Mount at root so the sub-app's internal /mcp route is matched directly.
# FastAPI exact routes (/health, etc.) still take priority over the mount.
app.mount("/", mcp.streamable_http_app())


if __name__ == "__main__":
    logging.info("IO River MCP server running on port %s", MCP_CONFIG_PORT)
    logging.info("MCP endpoint:  http://localhost:%s/mcp", MCP_CONFIG_PORT)
    logging.info("Health check:  http://localhost:%s/health", MCP_CONFIG_PORT)
    uvicorn.run(app, host="0.0.0.0", port=int(MCP_CONFIG_PORT), log_config=None)
