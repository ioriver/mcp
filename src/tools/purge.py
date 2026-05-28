import json
from typing import Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_purge_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(description="Get purge history for a service within a time range")
    async def get_purge_history(
        service_id: str,
        start_time: int,
        end_time: int,
    ) -> str:
        """Args:
            service_id: The service ID
            start_time: Start time as Unix timestamp in milliseconds
            end_time: End time as Unix timestamp in milliseconds
        """
        data = await get_client().get_purge_history(service_id, start_time, end_time)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Purge specific URLs or URL patterns from the CDN cache for a service")
    async def purge_cache(
        service_id: str,
        urls: list[str],
    ) -> str:
        """Args:
            service_id: The service ID
            urls: List of URL patterns to purge
        """
        await get_client().purge_cache(service_id, urls)
        return "Purge request submitted successfully"

    @mcp.tool(description="Purge cached content by cache tags for a service")
    async def purge_cache_tags(
        service_id: str,
        tags: list[str],
    ) -> str:
        """Args:
            service_id: The service ID
            tags: List of cache tags to purge
        """
        await get_client().purge_cache_tags(service_id, tags)
        return "Cache tag purge request submitted successfully"

    @mcp.tool(description="Purge all cached content for a service. Use with caution — this clears the entire cache.")
    async def purge_all(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        await get_client().purge_all(service_id)
        return "Full cache purge request submitted successfully"
