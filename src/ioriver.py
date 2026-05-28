# pylint: disable=invalid-name,too-many-positional-arguments

import asyncio
from typing import Any

import httpx

IORIVER_API_BASE = "https://manage.ioriver.io"


class IoRiverClient:
    """
    IO River API client scoped to a single request's token.

    The token arrives as "Bearer <token>" from mcp-remote and is forwarded
    to IO River as "Token <token>".
    """

    def __init__(self, bearer_token: str):
        # Strip "Bearer " prefix to get the raw token
        raw_token = bearer_token.removeprefix("Bearer ").removeprefix("bearer ").strip()
        self._headers = {
            "Authorization": f"Token {raw_token}",
            "Content-Type": "application/json",
        }

    async def _get(self, path: str, params: dict | None = None) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{IORIVER_API_BASE}{path}",
                headers=self._headers,
                params=params,
            )
            self._raise_for_status(response)
            return response.json()

    async def _post(self, path: str, body: dict) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{IORIVER_API_BASE}{path}",
                headers=self._headers,
                json=body,
            )
            self._raise_for_status(response)
            task_id = response.headers.get("x-background-task-id")
            if task_id:
                await self._await_background_task(int(task_id), response.headers.get("x-request-id", ""))
            return response.json()

    async def _put(self, path: str, body: dict) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.put(
                f"{IORIVER_API_BASE}{path}",
                headers=self._headers,
                json=body,
            )
            self._raise_for_status(response)
            task_id = response.headers.get("x-background-task-id")
            if task_id:
                await self._await_background_task(int(task_id), response.headers.get("x-request-id", ""))
            return response.json() if response.content else {}

    async def _delete(self, path: str) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(
                f"{IORIVER_API_BASE}{path}",
                headers=self._headers,
            )
            self._raise_for_status(response)
            task_id = response.headers.get("x-background-task-id")
            if task_id:
                await self._await_background_task(int(task_id), response.headers.get("x-request-id", ""))

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_error:
            request_id = response.headers.get("x-request-id")
            detail = f"{response.status_code} {response.reason_phrase}"
            if request_id:
                detail += f" (x-request-id: {request_id})"
            try:
                body = response.json()
                detail += f" — {body}"
            except Exception:
                if response.text:
                    detail += f" — {response.text}"
            raise httpx.HTTPStatusError(detail, request=response.request, response=response)

    async def _await_background_task(self, task_id: int, request_id: str) -> None:
        timeout = 3600
        elapsed = 0
        while elapsed < timeout:
            tasks = await self._get("/api/v1/async_tasks/")
            task = next((t for t in tasks if t["id"] == task_id), None)
            if task is None:
                # Task not found — assume it completed and was purged from the list
                return
            if task["status"] == "Status.COMPLETED":
                return
            if task["status"] == "Status.ERROR":
                raise RuntimeError(
                    f"Background task {task_id} failed: {task.get('message', '')} — {task.get('details', '')} (x-request-id: {request_id})"
                )
            await asyncio.sleep(1)
            elapsed += 1
        raise TimeoutError(f"Background task {task_id} did not complete within {timeout}s")

    # --- Services ---
    async def list_services(self) -> Any:
        return await self._get("/api/v1/services/")

    async def get_service(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/")

    async def create_service(self, data: dict) -> Any:
        return await self._post("/api/v1/services/", data)

    async def update_service(self, service_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/services/{service_id}/", data)

    async def delete_service(self, service_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/")

    # --- Domains & Origins ---
    async def list_domains(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/domains/")

    async def create_domain(self, service_id: str, data: dict) -> Any:
        return await self._post(f"/api/v1/services/{service_id}/domains/", data)

    async def update_domain(self, service_id: str, domain_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/services/{service_id}/domains/{domain_id}/", data)

    async def delete_domain(self, service_id: str, domain_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/domains/{domain_id}/")

    async def list_origins(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/origins/")

    async def create_origin(self, service_id: str, data: dict) -> Any:
        return await self._post(f"/api/v1/services/{service_id}/origins/", data)

    async def update_origin(self, service_id: str, origin_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/services/{service_id}/origins/{origin_id}/", data)

    async def delete_origin(self, service_id: str, origin_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/origins/{origin_id}/")

    # --- Service Certificates ---
    async def attach_certificate_to_service(self, service_id: str, certificate_id: str) -> Any:
        return await self._post(f"/api/v1/services/{service_id}/certificates/", {"certificate": certificate_id, "service": service_id})

    async def remove_certificate_from_service(self, service_id: str, service_certificate_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/certificates/{service_certificate_id}/")

    async def replace_certificate_in_service(self, service_id: str, service_certificate_id: str, new_certificate_id: str) -> Any:
        return await self._put(
            f"/api/v1/services/{service_id}/certificates/{service_certificate_id}/replace/",
            {"certificate": new_certificate_id, "service": service_id},
        )

    # --- Traffic Policies ---
    async def list_traffic_policies(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/traffic-policies/")

    async def get_traffic_policy(self, service_id: str, policy_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/traffic-policies/{policy_id}/")

    async def create_traffic_policy(self, service_id: str, data: dict) -> Any:
        return await self._post(f"/api/v1/services/{service_id}/traffic-policies/", data)

    async def update_traffic_policy(self, service_id: str, policy_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/services/{service_id}/traffic-policies/{policy_id}/", data)

    async def delete_traffic_policy(self, service_id: str, policy_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/traffic-policies/{policy_id}/")

    # --- Providers ---
    async def list_service_providers(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/providers/")

    async def add_service_provider(self, service_id: str, data: dict) -> Any:
        return await self._post(f"/api/v1/services/{service_id}/providers/", data)

    async def remove_service_provider(self, service_id: str, provider_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/providers/{provider_id}/")

    async def list_account_providers(self) -> Any:
        return await self._get("/api/v1/account-providers/")

    async def get_account_provider(self, provider_id: str) -> Any:
        return await self._get(f"/api/v1/account-providers/{provider_id}/")

    async def create_account_provider(self, data: dict) -> Any:
        return await self._post("/api/v1/account-providers/", data)

    async def update_account_provider(self, provider_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/account-providers/{provider_id}/", data)

    async def delete_account_provider(self, provider_id: str) -> None:
        await self._delete(f"/api/v1/account-providers/{provider_id}/")

    # --- Health & Performance ---
    async def list_health_checks(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/health-checks/")

    async def get_health_check(self, service_id: str, check_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/health-checks/{check_id}/")

    async def create_health_check(self, service_id: str, data: dict) -> Any:
        return await self._post(f"/api/v1/services/{service_id}/health-checks/", {**data, "service": service_id})

    async def update_health_check(self, service_id: str, check_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/services/{service_id}/health-checks/{check_id}/", {**data, "service": service_id})

    async def delete_health_check(self, service_id: str, check_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/health-checks/{check_id}/")

    async def list_performance_checks(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/performance-checks/")

    async def get_performance_check(self, service_id: str, check_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/performance-checks/{check_id}/")

    async def create_performance_check(self, service_id: str, data: dict) -> Any:
        return await self._post(f"/api/v1/services/{service_id}/performance-checks/", {**data, "service": service_id})

    async def update_performance_check(self, service_id: str, check_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/services/{service_id}/performance-checks/{check_id}/", {**data, "service": service_id})

    async def delete_performance_check(self, service_id: str, check_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/performance-checks/{check_id}/")

    # --- Analytics ---
    async def get_traffic_stats(self, service_id: str, start_time: int, end_time: int) -> Any:
        params = {"startTime": start_time, "endTime": end_time}
        return await self._get(f"/api/v2/traffic/overtime/{service_id}", params=params)

    # --- Alerts & Certificates ---
    async def list_alerts(self) -> Any:
        return await self._get("/api/v1/alerts/")

    async def list_certificates(self) -> Any:
        return await self._get("/api/v1/certificates/")

    async def get_certificate(self, certificate_id: str) -> Any:
        return await self._get(f"/api/v1/certificates/{certificate_id}/")

    async def create_certificate(self, data: dict) -> Any:
        return await self._post("/api/v1/certificates/", data)

    async def update_certificate(self, certificate_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/certificates/{certificate_id}/", data)

    async def delete_certificate(self, certificate_id: str) -> None:
        await self._delete(f"/api/v1/certificates/{certificate_id}/")

    async def _post_no_content(self, path: str, body: dict) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{IORIVER_API_BASE}{path}",
                headers=self._headers,
                json=body,
            )
            self._raise_for_status(response)

    # --- Cache Purge ---
    async def get_purge_history(self, service_id: str, start_time: int, end_time: int) -> Any:
        params = {"start_time": start_time, "end_time": end_time}
        return await self._get(f"/api/v1/purges/{service_id}", params=params)

    async def purge_cache(self, service_id: str, urls: list[str]) -> None:
        await self._post_no_content(f"/api/v1/purges/{service_id}/purge", {"patterns": urls})

    async def purge_cache_tags(self, service_id: str, tags: list[str]) -> None:
        await self._post_no_content(f"/api/v1/purges/{service_id}/purge-cache-tags", {"tags": tags})

    async def purge_all(self, service_id: str) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{IORIVER_API_BASE}/api/v1/purges/{service_id}/purge-all",
                headers=self._headers,
            )
            self._raise_for_status(response)

    # --- WAF Security Analytics ---
    @staticmethod
    def _build_waf_params(start: int, end: int, filters: list[dict]) -> dict[str, str | int]:
        params: dict[str, str | int] = {"start": start, "end": end}
        for f in filters:
            field = f["field"]
            operator = f.get("operator", "eq")
            value = f["value"]
            key = field if operator == "eq" else f"{field}~{operator}"
            params[key] = value
        return params

    async def get_security_requests_overtime(
        self,
        service_id: str,
        start: int,
        end: int,
        granularity: str,
        tz_offset: int,
        filters: list[dict],
    ) -> Any:
        params = self._build_waf_params(start, end, filters)
        params["granularity"] = granularity
        params["tz_offset"] = tz_offset
        return await self._get(f"/api/v1/events/waf/analytics/{service_id}/requests-overtime", params=params)

    async def get_security_top_stats(
        self,
        service_id: str,
        start: int,
        end: int,
        filters: list[dict],
    ) -> Any:
        params = self._build_waf_params(start, end, filters)
        return await self._get(f"/api/v1/events/waf/analytics/{service_id}/top-stats", params=params)

    async def get_security_sampled_logs(
        self,
        service_id: str,
        start: int,
        end: int,
        filters: list[dict],
        max_limit: int = 100,
    ) -> Any:
        params = self._build_waf_params(start, end, filters)
        params["max_limit"] = max_limit
        return await self._get(f"/api/v1/events/waf/analytics/{service_id}/sampled-logs", params=params)

    # --- Traffic Analytics ---
    @staticmethod
    def _build_traffic_params(
        start: int,
        end: int,
        granularity: str,
        measure_type: str,
        filters: list[dict],
    ) -> dict:
        params: dict = {
            "start": start,
            "end": end,
            "granularity": granularity,
            "measureType": measure_type,
        }
        for f in filters:
            field = f["field"]
            operator = f.get("operator", "eq")
            value = f["value"]
            key = field if operator == "eq" else f"{field}~{operator}"
            params[key] = value
        return params

    async def get_traffic_analytics_overtime(
        self,
        service_id: str,
        start: int,
        end: int,
        granularity: str,
        measure_type: str,
        tz_offset: int | None,
        filters: list[dict],
    ) -> Any:
        params = self._build_traffic_params(start, end, granularity, measure_type, filters)
        if tz_offset is not None:
            params["tz_offset"] = tz_offset
        return await self._get(f"/api/v1/advanced_stats/{service_id}/traffic-overtime", params=params)

    async def get_traffic_analytics_top_stats(
        self,
        service_id: str,
        start: int,
        end: int,
        granularity: str,
        measure_type: str,
        filters: list[dict],
    ) -> Any:
        params = self._build_traffic_params(start, end, granularity, measure_type, filters)
        return await self._get(f"/api/v1/advanced_stats/{service_id}/top-stats", params=params)

    async def get_traffic_analytics_sampled_logs(
        self,
        service_id: str,
        start: int,
        end: int,
        granularity: str,
        measure_type: str,
        filters: list[dict],
    ) -> Any:
        params = self._build_traffic_params(start, end, granularity, measure_type, filters)
        return await self._get(f"/api/v1/advanced_stats/{service_id}/sampled-logs", params=params)

    # --- Traffic Events ---
    async def get_traffic_events_for_service(
        self,
        service_id: str,
        start: int | None = None,
        end: int | None = None,
        locations: str | None = None,
        providers: str | None = None,
        codes: str | None = None,
        severities: str | None = None,
    ) -> Any:
        params = {k: v for k, v in {
            "start": start, "end": end, "locations": locations,
            "providers": providers, "codes": codes, "severities": severities,
        }.items() if v is not None}
        return await self._get(f"/api/v1/aggregated-events/service/{service_id}", params=params or None)

    async def get_traffic_events_for_account(
        self,
        account_id: str,
        start: int | None = None,
        end: int | None = None,
        locations: str | None = None,
        providers: str | None = None,
        codes: str | None = None,
        severities: str | None = None,
    ) -> Any:
        params = {k: v for k, v in {
            "start": start, "end": end, "locations": locations,
            "providers": providers, "codes": codes, "severities": severities,
        }.items() if v is not None}
        return await self._get(f"/api/v1/aggregated-events/account/{account_id}", params=params or None)

    # --- Behaviors ---
    async def list_behaviors(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/behaviors/")

    async def get_behavior(self, service_id: str, behavior_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/behaviors/{behavior_id}/")

    async def create_behavior(self, service_id: str, data: dict) -> Any:
        return await self._post(f"/api/v1/services/{service_id}/behaviors/", data)

    async def update_behavior(self, service_id: str, behavior_id: str, data: dict) -> Any:
        return await self._put(f"/api/v1/services/{service_id}/behaviors/{behavior_id}/", data)

    async def delete_behavior(self, service_id: str, behavior_id: str) -> None:
        await self._delete(f"/api/v1/services/{service_id}/behaviors/{behavior_id}/")

    # --- Geo Restrictions ---
    async def list_geo_restrictions(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/geo-restriction/")

    # --- Load Balancers ---
    async def list_load_balancers(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/load-balancers/")

    # --- Log Destinations ---
    async def list_log_destinations(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/log-destinations/")

    # --- Compute Functions ---
    async def list_compute_functions(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/compute/")

    # --- Protocol Config ---
    async def list_protocol_configs(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/protocol-config/")

    # --- URL Signing Keys ---
    async def list_url_signing_keys(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/url-signing-keys/")

    # --- WAF Rulesets ---
    async def list_waf_custom_rules(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/waf/custom/")

    async def list_waf_managed_rules(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/waf/managed/")

    async def list_waf_rate_limit_rules(self, service_id: str) -> Any:
        return await self._get(f"/api/v1/services/{service_id}/waf/rate-limit/")

    # --- Alert Channels ---
    async def list_alert_channels(self) -> Any:
        return await self._get("/api/v1/alert-channels/")

    async def test_alert(self, alert_id: str) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{IORIVER_API_BASE}/api/v1/alerts/{alert_id}/test_sending/",
                headers=self._headers,
            )
            self._raise_for_status(response)

    # --- Account Provider Commitments ---
    async def list_account_provider_commitments(self) -> Any:
        return await self._get("/api/v1/account-provider-commitment/")
