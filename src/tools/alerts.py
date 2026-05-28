import json
from typing import Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_alert_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(description="List all alerts configured in your IO River account")
    async def list_alerts() -> str:
        data = await get_client().list_alerts()
        return json.dumps(data, indent=2)

    @mcp.tool(description="List alert channels configured in the account (Slack, email, etc.)")
    async def list_alert_channels() -> str:
        data = await get_client().list_alert_channels()
        return json.dumps(data, indent=2)

    @mcp.tool(description="Test that an alert fires correctly by triggering a test notification")
    async def test_alert(alert_id: str) -> str:
        """Args:
            alert_id: The alert ID to test
        """
        await get_client().test_alert(alert_id)
        return "Alert test triggered successfully"
