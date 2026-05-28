import json
from typing import Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient

_CHECK_FIELDS = "name (required), url (required, must match one of the service's configured domains), enabled (optional, default true)"


def register_monitor_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    # --- Health Checks ---

    @mcp.tool(description="List all health checks for a service")
    async def list_health_checks(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_health_checks(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Get a specific health check by ID")
    async def get_health_check(service_id: str, check_id: str) -> str:
        """Args:
            service_id: The service ID
            check_id: The health check ID
        """
        data = await get_client().get_health_check(service_id, check_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description=f"Create a new health check for a service. Fields: {_CHECK_FIELDS}.")
    async def create_health_check(service_id: str, check: dict) -> str:
        """Args:
            service_id: The service ID
            check: Health check object with fields: name (required), url (required, must match one of the service's configured domains), enabled (optional)
        """
        data = await get_client().create_health_check(service_id, check)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Update an existing health check. Fetch it first, modify fields, then submit.")
    async def update_health_check(service_id: str, check_id: str, check: dict) -> str:
        """Args:
            service_id: The service ID
            check_id: The health check ID to update
            check: Full health check object with updated fields
        """
        data = await get_client().update_health_check(service_id, check_id, check)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Delete a health check from a service.")
    async def delete_health_check(service_id: str, check_id: str) -> str:
        """Args:
            service_id: The service ID
            check_id: The health check ID to delete
        """
        await get_client().delete_health_check(service_id, check_id)
        return "Health check deleted successfully"

    # --- Performance Checks ---

    @mcp.tool(description="List all performance checks for a service. Shows CDN performance metrics per region.")
    async def list_performance_checks(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_performance_checks(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Get a specific performance check by ID")
    async def get_performance_check(service_id: str, check_id: str) -> str:
        """Args:
            service_id: The service ID
            check_id: The performance check ID
        """
        data = await get_client().get_performance_check(service_id, check_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description=f"Create a new performance check for a service. Fields: {_CHECK_FIELDS}.")
    async def create_performance_check(service_id: str, check: dict) -> str:
        """Args:
            service_id: The service ID
            check: Performance check object with fields: name (required), url (required, must match one of the service's configured domains), enabled (optional)
        """
        data = await get_client().create_performance_check(service_id, check)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Update an existing performance check. Fetch it first, modify fields, then submit.")
    async def update_performance_check(service_id: str, check_id: str, check: dict) -> str:
        """Args:
            service_id: The service ID
            check_id: The performance check ID to update
            check: Full performance check object with updated fields
        """
        data = await get_client().update_performance_check(service_id, check_id, check)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Delete a performance check from a service.")
    async def delete_performance_check(service_id: str, check_id: str) -> str:
        """Args:
            service_id: The service ID
            check_id: The performance check ID to delete
        """
        await get_client().delete_performance_check(service_id, check_id)
        return "Performance check deleted successfully"
