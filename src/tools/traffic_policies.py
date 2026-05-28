import json
from typing import Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_traffic_policy_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(description=(
        "List all traffic policies for a service. "
        "There is exactly one default policy (is_default=true) covering the entire world — it can be created once and then only modified, never deleted. "
        "Additional geo-specific policies can be created, modified, and deleted to customize routing per region."
    ))
    async def list_traffic_policies(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_traffic_policies(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Get details of a specific traffic policy.")
    async def get_traffic_policy(service_id: str, policy_id: str) -> str:
        """Args:
            service_id: The service ID
            policy_id: The traffic policy ID
        """
        data = await get_client().get_traffic_policy(service_id, policy_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description=(
        "Create a new traffic policy for a service. "
        "There is exactly one default policy (is_default=true) which covers the entire world — it uses a catch-all geo [{continent: null, country: null, subdivision: null}] and can only be created once (then use update_traffic_policy to modify it). "
        "Geo-specific policies (is_default=false) can be created for custom regional routing and can later be modified or deleted. "
        "Required: type (Static/Dynamic/Cost based), providers (list of {service_provider, weight, priority}), "
        "geos (at least one entry required — use [{continent: null, country: null, subdivision: null}] for the default catch-all), "
        "health_checks (list of {health_check}, can be empty), "
        "performance_checks (list of {performance_check}, can be empty). "
        "Optional: failover, is_default, enable_performance_penalty, performance_penalty, asns."
    ))
    async def create_traffic_policy(service_id: str, policy: dict) -> str:
        """Args:
            service_id: The service ID
            policy: Traffic policy object. type is one of: Static, Dynamic, Cost based.
                    providers is a list of {service_provider (UUID), weight, priority}.
                    geos, health_checks, performance_checks can be empty lists.
        """
        data = await get_client().create_traffic_policy(service_id, {**policy, "service": service_id})
        return json.dumps(data, indent=2)

    @mcp.tool(description=(
        "Update an existing traffic policy. Fetch the policy first, modify fields, then submit. "
        "This is a full PUT replace — all required fields must be included. "
        "The default policy (is_default=true) can be modified but not deleted. "
        "Geo-specific policies can be freely modified."
    ))
    async def update_traffic_policy(service_id: str, policy_id: str, policy: dict) -> str:
        """Args:
            service_id: The service ID
            policy_id: The traffic policy ID to update
            policy: Full traffic policy object with updated fields
        """
        data = await get_client().update_traffic_policy(service_id, policy_id, policy)
        return json.dumps(data, indent=2)

    @mcp.tool(description=(
        "Delete a geo-specific traffic policy from a service. "
        "The default policy (is_default=true) cannot be deleted — use update_traffic_policy to modify it instead. "
        "Only geo-specific policies (is_default=false) can be deleted."
    ))
    async def delete_traffic_policy(service_id: str, policy_id: str) -> str:
        """Args:
            service_id: The service ID
            policy_id: The traffic policy ID to delete (must not be the default policy)
        """
        await get_client().delete_traffic_policy(service_id, policy_id)
        return "Traffic policy deleted successfully"
