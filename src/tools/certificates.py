import json
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_certificate_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(description="List all SSL/TLS certificates in your IO River account")
    async def list_certificates() -> str:
        data = await get_client().list_certificates()
        return json.dumps(data, indent=2)

    @mcp.tool(description="Get details of a specific certificate")
    async def get_certificate(certificate_id: str) -> str:
        """Args:
            certificate_id: The certificate ID
        """
        data = await get_client().get_certificate(certificate_id)
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Create a new SSL/TLS certificate. Three types are supported:\n"
            "- MANAGED: IO River creates and renews it. Provide 'name' and 'cn' (a JSON array of domains serialized as a string). "
            "Example: {\"name\": \"my-cert\", \"type\": \"MANAGED\", \"cn\": \"[\\\"example.com\\\", \\\"www.example.com\\\"]\"}\n"
            "- SELF_MANAGED: Import your own certificate. Provide 'name', 'certificate' (PEM), "
            "'certificate_chain' (PEM), and 'private_key' (PEM).\n"
            "- EXTERNAL: Certificate deployed directly in each provider. Provide 'name' and 'providers_certificates' list."
        )
    )
    async def create_certificate(certificate: dict[str, Any]) -> str:
        """Args:
            certificate: Certificate object. Required fields depend on type:
                MANAGED — name, type, cn
                SELF_MANAGED — name, type, certificate, certificate_chain, private_key
                EXTERNAL — name, type, providers_certificates
        """
        data = await get_client().create_certificate(certificate)
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Update an existing certificate (full replace via PUT). "
            "Fetch the current certificate first with get_certificate, modify the fields, then submit. "
            "Write-only fields (certificate, private_key, etc.) must be re-supplied on every update."
        )
    )
    async def update_certificate(certificate_id: str, certificate: dict[str, Any]) -> str:
        """Args:
            certificate_id: The certificate ID to update
            certificate: Full certificate object with all required fields
        """
        data = await get_client().update_certificate(certificate_id, certificate)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Delete a certificate from the account")
    async def delete_certificate(certificate_id: str) -> str:
        """Args:
            certificate_id: The certificate ID to delete
        """
        await get_client().delete_certificate(certificate_id)
        return "Certificate deleted successfully"
