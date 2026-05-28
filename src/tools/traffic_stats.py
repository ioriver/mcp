import json
from typing import Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_traffic_stats_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(description="Get traffic statistics over time for a service. Useful for analyzing performance and cost across CDN providers.")
    async def get_traffic_stats(
        service_id: str,
        start_time: int,
        end_time: int,
    ) -> str:
        """Args:
            service_id: The service ID
            start_time: Start time as a Unix timestamp in milliseconds e.g. 1778319300000
            end_time: End time as a Unix timestamp in milliseconds e.g. 1778322939410
        """
        data = await get_client().get_traffic_stats(service_id, start_time, end_time)
        return json.dumps(data, indent=2)
