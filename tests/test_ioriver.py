# pylint: disable=invalid-name

"""
Unit tests for IoRiverClient.

Covers:
  - Token stripping from the Authorization header
  - _raise_for_status: success, error without x-request-id, error with x-request-id
  - _build_waf_params: all operator types
  - _get / _post: correct URL, headers, params; error propagation
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from ioriver import IoRiverClient, IORIVER_API_BASE

SERVICE_ID = "aaaa-bbbb-cccc"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_http_client(response: MagicMock) -> MagicMock:
    """Return an httpx.AsyncClient mock that yields *response* from any call."""
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    mock.get = AsyncMock(return_value=response)
    mock.post = AsyncMock(return_value=response)
    return mock


def _ok_response(data, status: int = 200) -> MagicMock:
    r = MagicMock()
    r.is_error = False
    r.status_code = status
    r.reason_phrase = "OK"
    r.headers = {}
    r.json.return_value = data
    return r


def _error_response(status: int, request_id: str | None = None) -> MagicMock:
    r = MagicMock()
    r.is_error = True
    r.status_code = status
    r.reason_phrase = "Error"
    r.headers = {"x-request-id": request_id} if request_id else {}
    r.request = httpx.Request("GET", f"{IORIVER_API_BASE}/test")
    return r


# ---------------------------------------------------------------------------
# Token stripping
# ---------------------------------------------------------------------------

class TestTokenStripping:
    def test_bearer_prefix_stripped(self):
        client = IoRiverClient("Bearer mytoken")
        assert client._headers["Authorization"] == "Token mytoken"

    def test_lowercase_bearer_stripped(self):
        client = IoRiverClient("bearer mytoken")
        assert client._headers["Authorization"] == "Token mytoken"

    def test_raw_token_no_prefix(self):
        client = IoRiverClient("mytoken")
        assert client._headers["Authorization"] == "Token mytoken"

    def test_extra_whitespace_stripped(self):
        client = IoRiverClient("Bearer   mytoken  ")
        assert client._headers["Authorization"] == "Token mytoken"

    def test_content_type_set(self):
        client = IoRiverClient("Bearer mytoken")
        assert client._headers["Content-Type"] == "application/json"


# ---------------------------------------------------------------------------
# _raise_for_status
# ---------------------------------------------------------------------------

class TestRaiseForStatus:
    def _response(self, status: int, headers: dict | None = None) -> httpx.Response:
        req = httpx.Request("GET", f"{IORIVER_API_BASE}/test")
        return httpx.Response(status, headers=headers or {}, request=req)

    def test_2xx_does_not_raise(self):
        IoRiverClient._raise_for_status(self._response(200))
        IoRiverClient._raise_for_status(self._response(204))

    def test_4xx_raises(self):
        with pytest.raises(httpx.HTTPStatusError):
            IoRiverClient._raise_for_status(self._response(400))

    def test_5xx_raises(self):
        with pytest.raises(httpx.HTTPStatusError):
            IoRiverClient._raise_for_status(self._response(500))

    def test_error_message_includes_status(self):
        with pytest.raises(httpx.HTTPStatusError) as exc:
            IoRiverClient._raise_for_status(self._response(403))
        assert "403" in str(exc.value)

    def test_error_without_request_id_omits_header(self):
        with pytest.raises(httpx.HTTPStatusError) as exc:
            IoRiverClient._raise_for_status(self._response(400))
        assert "x-request-id" not in str(exc.value)

    def test_error_with_request_id_included(self):
        with pytest.raises(httpx.HTTPStatusError) as exc:
            IoRiverClient._raise_for_status(self._response(400, {"x-request-id": "abc-123"}))
        assert "x-request-id: abc-123" in str(exc.value)

    def test_500_with_request_id(self):
        with pytest.raises(httpx.HTTPStatusError) as exc:
            IoRiverClient._raise_for_status(self._response(500, {"x-request-id": "xyz-999"}))
        assert "500" in str(exc.value)
        assert "x-request-id: xyz-999" in str(exc.value)


# ---------------------------------------------------------------------------
# _build_waf_params
# ---------------------------------------------------------------------------

class TestBuildWafParams:
    def test_start_and_end_always_present(self):
        p = IoRiverClient._build_waf_params(1000, 2000, [])
        assert p["start"] == 1000
        assert p["end"] == 2000

    def test_no_filters_only_timestamps(self):
        p = IoRiverClient._build_waf_params(1, 2, [])
        assert len(p) == 2

    def test_eq_operator_no_tilde(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "action", "value": "block"}])
        assert p["action"] == "block"
        assert "action~eq" not in p

    def test_explicit_eq_operator_no_tilde(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "action", "operator": "eq", "value": "block"}])
        assert p["action"] == "block"
        assert "action~eq" not in p

    def test_neq_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "action", "operator": "neq", "value": "allow"}])
        assert p["action~neq"] == "allow"

    def test_in_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "country", "operator": "in", "value": "CN,BE,PT"}])
        assert p["country~in"] == "CN,BE,PT"

    def test_not_in_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "method", "operator": "!in", "value": "PUT,POST"}])
        assert p["method~!in"] == "PUT,POST"

    def test_gte_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "status_code", "operator": "gte", "value": "400"}])
        assert p["status_code~gte"] == "400"

    def test_lte_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "status_code", "operator": "lte", "value": "499"}])
        assert p["status_code~lte"] == "499"

    def test_contains_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "query_string", "operator": "contains", "value": "test"}])
        assert p["query_string~contains"] == "test"

    def test_not_contains_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "host", "operator": "!contains", "value": "example"}])
        assert p["host~!contains"] == "example"

    def test_starts_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "path", "operator": "starts", "value": "/api"}])
        assert p["path~starts"] == "/api"

    def test_ends_operator(self):
        p = IoRiverClient._build_waf_params(0, 1, [{"field": "host", "operator": "ends", "value": ".example.com"}])
        assert p["host~ends"] == ".example.com"

    def test_multiple_filters(self):
        filters = [
            {"field": "action", "value": "block"},
            {"field": "country", "operator": "in", "value": "CN,BE"},
            {"field": "status_code", "operator": "gte", "value": "400"},
        ]
        p = IoRiverClient._build_waf_params(1000, 2000, filters)
        assert p["action"] == "block"
        assert p["country~in"] == "CN,BE"
        assert p["status_code~gte"] == "400"
        assert p["start"] == 1000
        assert p["end"] == 2000


# ---------------------------------------------------------------------------
# _get / _post URL and param construction
# ---------------------------------------------------------------------------

class TestClientRequests:
    async def test_list_services_url(self):
        client = IoRiverClient("Bearer tok")
        mock = _mock_http_client(_ok_response([{"id": "s1"}]))
        with patch("httpx.AsyncClient", return_value=mock):
            result = await client.list_services()
        mock.get.assert_called_once_with(
            f"{IORIVER_API_BASE}/api/v1/services/",
            headers=client._headers,
            params=None,
        )
        assert result == [{"id": "s1"}]

    async def test_get_service_url(self):
        client = IoRiverClient("Bearer tok")
        mock = _mock_http_client(_ok_response({"id": SERVICE_ID}))
        with patch("httpx.AsyncClient", return_value=mock):
            await client.get_service(SERVICE_ID)
        mock.get.assert_called_once_with(
            f"{IORIVER_API_BASE}/api/v1/services/{SERVICE_ID}/",
            headers=client._headers,
            params=None,
        )

    async def test_list_domains_url(self):
        client = IoRiverClient("Bearer tok")
        mock = _mock_http_client(_ok_response([]))
        with patch("httpx.AsyncClient", return_value=mock):
            await client.list_domains(SERVICE_ID)
        mock.get.assert_called_once_with(
            f"{IORIVER_API_BASE}/api/v1/services/{SERVICE_ID}/domains/",
            headers=client._headers,
            params=None,
        )

    async def test_list_origins_url(self):
        client = IoRiverClient("Bearer tok")
        mock = _mock_http_client(_ok_response([]))
        with patch("httpx.AsyncClient", return_value=mock):
            await client.list_origins(SERVICE_ID)
        mock.get.assert_called_once_with(
            f"{IORIVER_API_BASE}/api/v1/services/{SERVICE_ID}/origins/",
            headers=client._headers,
            params=None,
        )

    async def test_get_traffic_stats_params(self):
        client = IoRiverClient("Bearer tok")
        mock = _mock_http_client(_ok_response({}))
        with patch("httpx.AsyncClient", return_value=mock):
            await client.get_traffic_stats(SERVICE_ID, 1_000_000, 2_000_000)
        mock.get.assert_called_once_with(
            f"{IORIVER_API_BASE}/api/v2/traffic/overtime/{SERVICE_ID}",
            headers=client._headers,
            params={"startTime": 1_000_000, "endTime": 2_000_000},
        )

    async def test_purge_cache_post_body(self):
        client = IoRiverClient("Bearer tok")
        urls = ["https://example.com/page"]
        # purge returns 204 No Content; purge_cache does not call .json()
        mock = _mock_http_client(_ok_response(None, status=204))
        with patch("httpx.AsyncClient", return_value=mock):
            await client.purge_cache(SERVICE_ID, urls)
        mock.post.assert_called_once_with(
            f"{IORIVER_API_BASE}/api/v1/purges/{SERVICE_ID}/purge",
            headers=client._headers,
            json={"patterns": urls},
        )

    async def test_get_security_requests_overtime_params(self):
        client = IoRiverClient("Bearer tok")
        mock = _mock_http_client(_ok_response({"points": []}))
        filters = [
            {"field": "action", "value": "block"},
            {"field": "country", "operator": "in", "value": "CN,US"},
        ]
        with patch("httpx.AsyncClient", return_value=mock):
            await client.get_security_requests_overtime(SERVICE_ID, 1000, 2000, "hour", 3600000, filters)
        params = mock.get.call_args.kwargs["params"]
        assert params["start"] == 1000
        assert params["end"] == 2000
        assert params["granularity"] == "hour"
        assert params["tz_offset"] == 3600000
        assert params["action"] == "block"
        assert params["country~in"] == "CN,US"

    async def test_get_security_top_stats_url(self):
        client = IoRiverClient("Bearer tok")
        mock = _mock_http_client(_ok_response({}))
        with patch("httpx.AsyncClient", return_value=mock):
            await client.get_security_top_stats(SERVICE_ID, 1000, 2000, [])
        url = mock.get.call_args.args[0]
        assert url == f"{IORIVER_API_BASE}/api/v1/events/waf/analytics/{SERVICE_ID}/top-stats"

    async def test_get_security_sampled_logs_max_limit(self):
        client = IoRiverClient("Bearer tok")
        mock = _mock_http_client(_ok_response([]))
        with patch("httpx.AsyncClient", return_value=mock):
            await client.get_security_sampled_logs(SERVICE_ID, 1000, 2000, [], max_limit=50)
        params = mock.get.call_args.kwargs["params"]
        assert params["max_limit"] == 50

    async def test_error_propagates_with_request_id(self):
        client = IoRiverClient("Bearer tok")
        err_response = _error_response(403, request_id="req-xyz")
        mock = _mock_http_client(err_response)
        with patch("httpx.AsyncClient", return_value=mock):
            with pytest.raises(httpx.HTTPStatusError) as exc:
                await client.list_services()
        assert "x-request-id: req-xyz" in str(exc.value)

    async def test_error_without_request_id(self):
        client = IoRiverClient("Bearer tok")
        err_response = _error_response(500)
        mock = _mock_http_client(err_response)
        with patch("httpx.AsyncClient", return_value=mock):
            with pytest.raises(httpx.HTTPStatusError) as exc:
                await client.list_services()
        assert "x-request-id" not in str(exc.value)
