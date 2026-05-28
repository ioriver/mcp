# pylint: disable=too-many-positional-arguments
import json
from typing import Callable, Literal

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient


def register_security_analytics_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(
        description=(
            "Get WAF request counts over time for a service based on applied filters. "
            "Useful for visualizing attack trends. "
            "end must not be in the future — use the current Unix timestamp in milliseconds as the maximum. "
            "Filter fields: ip, host, path, asn, device_type, user_agent, os, query_string, "
            "browser, referer, method, country, http_version, mitigation_type, action, "
            "tls_version, custom_rule, rate_limiting_rule, status_code, request_id, ja3. "
            "All fields support operators: eq (default), neq, in, !in. "
            "Text fields (host, path, referer, query_string, user_agent) also support: "
            "contains, !contains, starts, !starts, ends, !ends. "
            "status_code supports: gte, lte."
        )
    )
    async def get_security_requests_overtime(
        service_id: str,
        start: int,
        end: int,
        granularity: Literal["hour", "day", "month"] = "hour",
        tz_offset: int = 0,
        filters: list[dict] | None = None,
    ) -> str:
        """Args:
            service_id: The service ID
            start: Start time as Unix timestamp in milliseconds
            end: End time as Unix timestamp in milliseconds — must not be in the future
            tz_offset: Timezone offset in milliseconds e.g. 10800000 for UTC+3
            filters: List of filter objects, each with:
                - field: ip | host | path | asn | device_type | user_agent | os |
                         query_string | browser | referer | method | country |
                         http_version | mitigation_type | action | tls_version |
                         custom_rule | rate_limiting_rule | status_code | request_id | ja3
                - operator (optional, default eq): eq | neq | in | !in |
                         contains | !contains | starts | !starts | ends | !ends | gte | lte
                - value: for in/!in use comma-separated e.g. "CN,BE,PT"
            Examples:
                [{"field": "action", "value": "block"},
                 {"field": "country", "operator": "in", "value": "CN,BE,PT"},
                 {"field": "method", "operator": "!in", "value": "PUT,POST"},
                 {"field": "status_code", "operator": "gte", "value": "400"},
                 {"field": "query_string", "operator": "contains", "value": "test"}]
        """
        data = await get_client().get_security_requests_overtime(
            service_id=service_id,
            start=start,
            end=end,
            granularity=granularity,
            tz_offset=tz_offset,
            filters=filters or [],
        )
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Get WAF top statistics for a service — returns the top 5 values for each "
            "request property (country, browser, IP, method, etc.) matching the filter. "
            "end must not be in the future — use the current Unix timestamp in milliseconds as the maximum. "
            "Accepts the same filter schema as get_security_requests_overtime."
        )
    )
    async def get_security_top_stats(
        service_id: str,
        start: int,
        end: int,
        filters: list[dict] | None = None,
    ) -> str:
        """Args:
            service_id: The service ID
            start: Start time as Unix timestamp in milliseconds
            end: End time as Unix timestamp in milliseconds — must not be in the future
            filters: Same filter schema as get_security_requests_overtime
        """
        data = await get_client().get_security_top_stats(
            service_id=service_id,
            start=start,
            end=end,
            filters=filters or [],
        )
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Get WAF sampled raw logs for a service matching the applied filter. "
            "Returns individual request records up to max_limit. "
            "end must not be in the future — use the current Unix timestamp in milliseconds as the maximum. "
            "Accepts the same filter schema as get_security_requests_overtime."
        )
    )
    async def get_security_sampled_logs(
        service_id: str,
        start: int,
        end: int,
        max_limit: int = 100,
        filters: list[dict] | None = None,
    ) -> str:
        """Args:
            service_id: The service ID
            start: Start time as Unix timestamp in milliseconds
            end: End time as Unix timestamp in milliseconds — must not be in the future
            max_limit: Maximum number of log entries to return (default: 100)
            filters: Same filter schema as get_security_requests_overtime
        """
        data = await get_client().get_security_sampled_logs(
            service_id=service_id,
            start=start,
            end=end,
            filters=filters or [],
            max_limit=max_limit,
        )
        return json.dumps(data, indent=2)
