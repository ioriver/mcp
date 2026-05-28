# pylint: disable=too-many-positional-arguments
import json
from typing import Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_event_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(
        description=(
            "Get aggregated traffic events for a specific service. "
            "Events include CDN provider issues, health check failures, and routing changes. "
            "Filter by time range (Unix ms), locations (ISO3166-2 codes), providers, event codes, or severities."
        )
    )
    async def get_traffic_events_for_service(
        service_id: str,
        start: int | None = None,
        end: int | None = None,
        locations: str | None = None,
        providers: str | None = None,
        codes: str | None = None,
        severities: str | None = None,
    ) -> str:
        """Args:
            service_id: The service ID
            start: Start time in Unix milliseconds (requires end)
            end: End time in Unix milliseconds (requires start)
            locations: Comma-separated ISO3166-2 location codes to filter by
            providers: Comma-separated CDN provider names to filter by
            codes: Comma-separated event codes to include
            severities: Comma-separated severity levels to include
        """
        data = await get_client().get_traffic_events_for_service(
            service_id, start=start, end=end, locations=locations,
            providers=providers, codes=codes, severities=severities,
        )
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Get aggregated traffic events for the entire account (all services). "
            "Filter by time range (Unix ms), locations (ISO3166-2 codes), providers, event codes, or severities."
        )
    )
    async def get_traffic_events_for_account(
        account_id: str,
        start: int | None = None,
        end: int | None = None,
        locations: str | None = None,
        providers: str | None = None,
        codes: str | None = None,
        severities: str | None = None,
    ) -> str:
        """Args:
            account_id: The account ID (UUID)
            start: Start time in Unix milliseconds (requires end)
            end: End time in Unix milliseconds (requires start)
            locations: Comma-separated ISO3166-2 location codes to filter by
            providers: Comma-separated CDN provider names to filter by
            codes: Comma-separated event codes to include
            severities: Comma-separated severity levels to include
        """
        data = await get_client().get_traffic_events_for_account(
            account_id, start=start, end=end, locations=locations,
            providers=providers, codes=codes, severities=severities,
        )
        return json.dumps(data, indent=2)
