import json
from typing import Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_account_provider_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(description="List all CDN providers connected to your IO River account (e.g. Cloudflare, Akamai, Fastly)")
    async def list_account_providers() -> str:
        data = await get_client().list_account_providers()
        return json.dumps(data, indent=2)

    @mcp.tool(description="Get details of a specific account provider by ID")
    async def get_account_provider(provider_id: str) -> str:
        """Args:
            provider_id: The account provider ID
        """
        data = await get_client().get_account_provider(provider_id)
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Add a CDN provider to the IO River account. "
            "provider field (int): Cloudflare=2, Cloudfront=3, AzureCDN=4, Akamai=5, "
            "Fastly=13, Edgio=15, GCPCloudCDN=17, GCPMediaCDN=18. "
            "credentials format varies by provider: "
            "Fastly/Cloudflare/GCP: string (API token / service account JSON). "
            "Cloudfront: {accessKey, accessSecret} or {assume_role_arn, external_id}. "
            "AzureCDN: {subscriptionId, clientId, tenantId, clientSecret, resourceGroupName}. "
            "Akamai: {client_token, client_secret, access_secret, base_url}."
        )
    )
    async def create_account_provider(provider: dict) -> str:
        """Args:
            provider: Object with fields: provider (int, required), credentials (required),
                      display_name (optional string)
        """
        data = await get_client().create_account_provider(provider)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Update an existing account provider. Fetch the provider first, modify credentials or display_name, then submit.")
    async def update_account_provider(provider_id: str, provider: dict) -> str:
        """Args:
            provider_id: The account provider ID
            provider: Full provider object with updated fields
        """
        data = await get_client().update_account_provider(provider_id, provider)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Remove a CDN provider from the IO River account permanently.")
    async def delete_account_provider(provider_id: str) -> str:
        """Args:
            provider_id: The account provider ID to remove
        """
        await get_client().delete_account_provider(provider_id)
        return "Account provider deleted successfully"
