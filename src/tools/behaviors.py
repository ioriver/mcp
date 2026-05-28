import json
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_behavior_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(description="List all behaviors (cache/routing rules) for a service")
    async def list_behaviors(service_id: str) -> str:
        """Args:
            service_id: The service ID
        """
        data = await get_client().list_behaviors(service_id)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Get details of a specific behavior")
    async def get_behavior(service_id: str, behavior_id: str) -> str:
        """Args:
            service_id: The service ID
            behavior_id: The behavior ID
        """
        data = await get_client().get_behavior(service_id, behavior_id)
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Create a new behavior for a service. "
            "A behavior defines cache/routing rules applied to requests matching a path pattern. "
            "The 'behavior_actions' array contains the actual rules. "
            "Each action requires a 'type' field. Available action types and their key fields:\n"
            "- CACHE_TTL: max_ttl (seconds)\n"
            "- CACHE_BEHAVIOR: cache_behavior_value (CACHE | BYPASS | NO_STORE)\n"
            "- CACHED_METHODS: cached_methods (e.g. GET,HEAD)\n"
            "- ALLOWED_METHODS: allowed_methods (e.g. GET,HEAD,POST)\n"
            "- CACHE_KEY: cache_key (JSON string with headers/cookies/query_strings config)\n"
            "- STATUS_CODE_CACHE: status_code (4 for 4xx, 5 for 5xx), max_ttl, cache_behavior_value\n"
            "- STATUS_CODE_BROWSER_CACHE: status_code, max_ttl\n"
            "- SET_RESPONSE_HEADER: response_header_name, response_header_value\n"
            "- DELETE_RESPONSE_HEADER: response_header_name\n"
            "- SET_REQUEST_HEADER: request_header_name, request_header_value\n"
            "- DELETE_REQUEST_HEADER: request_header_name\n"
            "- FORWARD_CLIENT_HEADER: request_header_name (forwards client header to origin)\n"
            "- HOST_HEADER_OVERRIDE: host_header or use_domain_origin (bool)\n"
            "- COMPRESSION: enabled (bool)\n"
            "- BROWSER_CACHE_TTL: max_ttl (seconds)\n"
            "- STALE_TTL: max_ttl (seconds, serve stale content while revalidating)\n"
            "- ORIGIN_CACHE_CONTROL: origin_cache_control_enabled (bool)\n"
            "- REDIRECT: redirect_url, status_code (301 or 302)\n"
            "- URL_REWRITE: url_rewrite_destination\n"
            "- BYPASS_CACHE_ON_COOKIE: pattern (cookie name pattern)\n"
            "- OVERRIDE_ORIGIN: origin (UUID of origin to use)\n"
            "- LARGE_FILES_OPTIMIZATION: enabled (bool)\n"
            "- FOLLOW_REDIRECTS: enabled (bool)\n"
            "- ORIGIN_ERRORS_PASS_THRU: enabled (bool)\n"
            "- VIEWER_PROTOCOL: viewer_protocol (HTTP_AND_HTTPS | HTTPS_ONLY | REDIRECT_HTTP_TO_HTTPS)\n"
            "- SET_CORS_HEADER: cors_allow_origin_domain (bool)\n"
            "- GENERATE_PREFLIGHT_RESPONSE: generate_preflight_allowed_headers\n"
            "- GENERATE_RESPONSE: response_page_path, status_code\n"
            "- TRUE_CLIENT_IP: enabled (bool)\n"
            "- STREAM_LOGS: unified_log_destination (UUID), unified_log_sampling_rate\n"
            "- URL_SIGNING: enabled (bool)\n"
            "- DENY_ACCESS: enabled (bool)\n"
            "- DENY_ACCESS_BY_IP: deny_access_by_ip (object with ip_list)\n"
            "- ALLOW_ACCESS_ONLY_FROM_IP: allow_access_only_from_ip (object with ip_list)\n"
            "- DENY_ACCESS_BY_TIME: deny_access_by_time (object with date_time_window or time_periodic)\n"
            "All actions also accept: allowed_methods, cached_methods, cors_allow_origin_domain, viewer_protocol, override_header_value, enable_websockets."
        )
    )
    async def create_behavior(service_id: str, behavior: dict[str, Any]) -> str:
        """Args:
            service_id: The service ID
            behavior: Behavior object with fields: name (required), path_pattern, service (required),
                      behavior_actions (required array), is_default, additional_paths, complex_condition
        """
        data = await get_client().create_behavior(service_id, behavior)
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Update an existing behavior. Replaces the entire behavior object (PUT). "
            "Fetch the current behavior first with get_behavior, modify the fields, then submit. "
            "See create_behavior for the full list of available action types."
        )
    )
    async def update_behavior(service_id: str, behavior_id: str, behavior: dict[str, Any]) -> str:
        """Args:
            service_id: The service ID
            behavior_id: The behavior ID to update
            behavior: Full behavior object with all required fields (name, service, behavior_actions)
        """
        data = await get_client().update_behavior(service_id, behavior_id, behavior)
        return json.dumps(data, indent=2)

    @mcp.tool(description="Delete a behavior from a service")
    async def delete_behavior(service_id: str, behavior_id: str) -> str:
        """Args:
            service_id: The service ID
            behavior_id: The behavior ID to delete
        """
        await get_client().delete_behavior(service_id, behavior_id)
        return "Behavior deleted successfully"
