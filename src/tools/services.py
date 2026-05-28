import json
from typing import Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_service_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(description="List all IO River services in your account")
    async def list_services() -> str:
        data = await get_client().list_services()
        return json.dumps(data, indent=2)

    @mcp.tool(description="Get details of a specific IO River service")
    async def get_service(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().get_service(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Create a new IO River service. Required: name (alphanumeric, dashes, underscores, spaces). Optional: description.")
    async def create_service(service: dict) -> str:
        """Args:
            service: Service object with fields: name (required), description (optional)
        """
        data = await get_client().create_service(service)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Update an existing service. Fetch the service first, modify fields, then submit. Writable fields: name, description.")
    async def update_service(service_id: str, service: dict) -> str:
        """Args:
            service_id: The service ID
            service: Full service object with updated fields (name required)
        """
        data = await get_client().update_service(service_id, service)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Delete a service permanently.")
    async def delete_service(service_id: str) -> str:
        """Args:
            service_id: The service ID to delete
        """
        await get_client().delete_service(service_id)
        return "Service deleted successfully"

    @mcp.tool(description="List all domains for a specific service")
    async def list_domains(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_domains(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Add a domain to a service. Required: domain (hostname string), aliases (list, can be empty), mappings (list of {target_id, target_type} objects, can be empty).")
    async def create_domain(service_id: str, domain: dict) -> str:
        """Args:
            service_id: The service ID
            domain: Domain object with fields: domain (required), aliases (required, list), mappings (required, list)
        """
        data = await get_client().create_domain(service_id, domain)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Update an existing domain on a service. Fetch the domain first, modify fields, then submit.")
    async def update_domain(service_id: str, domain_id: str, domain: dict) -> str:
        """Args:
            service_id: The service ID
            domain_id: The domain ID to update
            domain: Full domain object with updated fields
        """
        data = await get_client().update_domain(service_id, domain_id, domain)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Delete a domain from a service.")
    async def delete_domain(service_id: str, domain_id: str) -> str:
        """Args:
            service_id: The service ID
            domain_id: The domain ID to delete
        """
        await get_client().delete_domain(service_id, domain_id)
        return "Domain deleted successfully"

    @mcp.tool(description="List all origins (backend servers) for a specific service")
    async def list_origins(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_origins(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Add an origin (backend server) to a service. Required: host. Optional: protocol (HTTP/HTTPS/MATCH), http_port, https_port, path, verify_tls, timeout_ms.")
    async def create_origin(service_id: str, origin: dict) -> str:
        """Args:
            service_id: The service ID
            origin: Origin object with fields: host (required, hostname or IP), protocol (optional, default HTTP), http_port, https_port, path, verify_tls, timeout_ms
        """
        data = await get_client().create_origin(service_id, origin)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Update an existing origin on a service. Fetch the origin first, modify fields, then submit.")
    async def update_origin(service_id: str, origin_id: str, origin: dict) -> str:
        """Args:
            service_id: The service ID
            origin_id: The origin ID to update
            origin: Full origin object with updated fields
        """
        data = await get_client().update_origin(service_id, origin_id, origin)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Delete an origin from a service.")
    async def delete_origin(service_id: str, origin_id: str) -> str:
        """Args:
            service_id: The service ID
            origin_id: The origin ID to delete
        """
        await get_client().delete_origin(service_id, origin_id)
        return "Origin deleted successfully"

    @mcp.tool(description="List all CDN providers attached to a specific service")
    async def list_service_providers(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_service_providers(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Add a CDN provider to a service. Required: account_provider (UUID of the account provider to attach). Optional: cname, display_name, is_unmanaged.")
    async def add_service_provider(service_id: str, provider: dict) -> str:
        """Args:
            service_id: The service ID
            provider: Provider object with fields: account_provider (required, UUID), cname (optional), display_name (optional), is_unmanaged (optional, default false)
        """
        data = await get_client().add_service_provider(service_id, {**provider, "service": service_id})
        return json.dumps(data, indent=2)

    @mcp.tool(description="Remove a CDN provider from a service. Will fail if the provider is referenced in any traffic policy — remove it from all traffic policies first.")
    async def remove_service_provider(service_id: str, provider_id: str) -> str:
        """Args:
            service_id: The service ID
            provider_id: The service-provider ID to remove
        """
        policies = await get_client().list_traffic_policies(service_id)
        referencing = [
            p["id"] for p in policies
            if any(pp["service_provider"] == provider_id for pp in p.get("providers", []))
        ]
        if referencing:
            return (
                f"Cannot remove provider: it is still referenced in traffic "
                f"policy/policies: {referencing}. Remove it from those policies first."
            )
        await get_client().remove_service_provider(service_id, provider_id)
        return "Service provider removed successfully"

    @mcp.tool(description="Attach a certificate to a service.")
    async def attach_certificate_to_service(service_id: str, certificate_id: str) -> str:
        """Args:
            service_id: The service ID
            certificate_id: The certificate ID to attach
        """
        data = await get_client().attach_certificate_to_service(service_id, certificate_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Remove a certificate from a service. Use list_service to find the service_certificate_id (different from the certificate ID).")
    async def remove_certificate_from_service(service_id: str, service_certificate_id: str) -> str:
        """Args:
            service_id: The service ID
            service_certificate_id: The service-certificate association ID (not the certificate ID itself)
        """
        await get_client().remove_certificate_from_service(service_id, service_certificate_id)
        return "Certificate removed from service successfully"

    @mcp.tool(description="Replace a certificate in a service with a different certificate. The service_certificate_id is the association ID, not the certificate ID.")
    async def replace_certificate_in_service(service_id: str, service_certificate_id: str, new_certificate_id: str) -> str:
        """Args:
            service_id: The service ID
            service_certificate_id: The existing service-certificate association ID to replace
            new_certificate_id: The new certificate ID to use instead
        """
        data = await get_client().replace_certificate_in_service(service_id, service_certificate_id, new_certificate_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="List geo restrictions for a service. Geo restrictions allow or deny traffic from specific countries.")
    async def list_geo_restrictions(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_geo_restrictions(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="List unified log destinations for a service (S3-compatible log export configurations)")
    async def list_log_destinations(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_log_destinations(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="List protocol configurations for a service (HTTP/2, HTTP/3, IPv6 settings)")
    async def list_protocol_configs(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_protocol_configs(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="List URL signing keys for a service (used for signed URL security)")
    async def list_url_signing_keys(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_url_signing_keys(service_id)
        return json.dumps(data, indent=2)
