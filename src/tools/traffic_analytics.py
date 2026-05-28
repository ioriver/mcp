# pylint: disable=too-many-positional-arguments
import json
from typing import Callable, Literal

from mcp.server.fastmcp import FastMCP

from ioriver import IoRiverClient

_FILTER_FIELDS = (
    "country, asn, host, provider, user_agent, method, status_code, path, "
    "ip, device_type, os, browser, referer, http_version, cache_status, continent"
)

_FILTER_NOTE = (
    f"Supported filter fields: {_FILTER_FIELDS}. "
    "All fields support operators: eq (default), neq, in, !in. "
    "Text fields (host, path, user_agent, referer) also support: "
    "contains, !contains, starts, !starts, ends, !ends. "
    "status_code supports: gte, lte."
)

_MEASURE_TYPES = '"requests", "bytes"'


def register_traffic_analytics_tools(mcp: FastMCP, get_client: Callable[[], IoRiverClient]) -> None:

    @mcp.tool(
        description=(
            "Get CDN traffic request/bandwidth metrics over time for a service. "
            "end must not be in the future — use the current Unix timestamp in milliseconds as the maximum. "
            f"measureType controls the metric: {_MEASURE_TYPES}. "
            f"{_FILTER_NOTE} "
            "Returns time-series data bucketed by granularity."
        )
    )
    async def get_traffic_analytics_overtime(
        service_id: str,
        start: int,
        end: int,
        granularity: Literal["hour", "day", "month"] = "hour",
        measure_type: str = "requests",
        tz_offset: int | None = None,
        filters: list[dict] | None = None,
    ) -> str:
        """Args:
            service_id: The service ID
            start: Start time as Unix timestamp in milliseconds
            end: End time as Unix timestamp in milliseconds — must not be in the future
            granularity: Time bucket size: hour, day, or month
            measure_type: Metric to measure: requests | bytes
            tz_offset: Timezone offset in milliseconds e.g. 10800000 for UTC+3
            filters: List of filter objects, each with:
                - field: country | asn | host | provider | user_agent | method | status_code |
                         path | ip | device_type | os | browser | referer | http_version |
                         cache_status | continent
                - operator (optional, default eq): eq | neq | in | !in |
                         contains | !contains | starts | !starts | ends | !ends | gte | lte
                - value: string; for in/!in use comma-separated e.g. "US,SG"
        """
        data = await get_client().get_traffic_analytics_overtime(
            service_id=service_id,
            start=start,
            end=end,
            granularity=granularity,
            measure_type=measure_type,
            tz_offset=tz_offset,
            filters=filters or [],
        )
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Get top CDN traffic statistics for a service — returns the top values for each "
            "dimension (country, provider, host, user_agent, etc.) for the given time range. "
            "end must not be in the future — use the current Unix timestamp in milliseconds as the maximum. "
            f"measureType controls the metric: {_MEASURE_TYPES}. "
            f"{_FILTER_NOTE}"
        )
    )
    async def get_traffic_analytics_top_stats(
        service_id: str,
        start: int,
        end: int,
        granularity: Literal["hour", "day", "month"] = "hour",
        measure_type: str = "requests",
        filters: list[dict] | None = None,
    ) -> str:
        """Args:
            service_id: The service ID
            start: Start time as Unix timestamp in milliseconds
            end: End time as Unix timestamp in milliseconds — must not be in the future
            granularity: Time bucket size: hour, day, or month
            measure_type: Metric to measure: requests | bytes
            filters: Same filter schema as get_traffic_analytics_overtime
        """
        data = await get_client().get_traffic_analytics_top_stats(
            service_id=service_id,
            start=start,
            end=end,
            granularity=granularity,
            measure_type=measure_type,
            filters=filters or [],
        )
        return json.dumps(data, indent=2)

    @mcp.tool(
        description=(
            "Get sampled CDN traffic log entries for a service matching the applied filters. "
            "Returns individual request records for detailed inspection. "
            "end must not be in the future — use the current Unix timestamp in milliseconds as the maximum. "
            f"measureType controls the metric: {_MEASURE_TYPES}. "
            f"{_FILTER_NOTE}"
        )
    )
    async def get_traffic_analytics_sampled_logs(
        service_id: str,
        start: int,
        end: int,
        granularity: Literal["hour", "day", "month"] = "hour",
        measure_type: str = "requests",
        filters: list[dict] | None = None,
    ) -> str:
        """Args:
            service_id: The service ID
            start: Start time as Unix timestamp in milliseconds
            end: End time as Unix timestamp in milliseconds — must not be in the future
            granularity: Time bucket size: hour, day, or month
            measure_type: Metric to measure: requests | bytes
            filters: Same filter schema as get_traffic_analytics_overtime
        """
        data = await get_client().get_traffic_analytics_sampled_logs(
            service_id=service_id,
            start=start,
            end=end,
            granularity=granularity,
            measure_type=measure_type,
            filters=filters or [],
        )
        return json.dumps(data, indent=2)
