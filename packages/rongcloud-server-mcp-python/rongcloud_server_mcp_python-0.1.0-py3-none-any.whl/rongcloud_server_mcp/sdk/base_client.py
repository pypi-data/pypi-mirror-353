import hashlib
import json
import time
from typing import Any, Dict, Optional

import httpx
from rongcloud_server_mcp.version import __version__
from .exceptions import APIErrorDetail, RongCloudAPIError, RongCloudRequestError

DEFAULT_HEADERS = {
    "User-Agent": "rongcloud-server-mcp-python/"+__version__
}

class BaseClient:
    """RongCloud Base Client (Core HTTP functionality).

    Documentation: https://www.rongcloud.cn/docs/push_server.html
    """

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        api_base: str = 'https://api.rong-api.com',
        timeout: float = 10.0,
    ):
        """Initialize the RongCloud client.

        Args:
            app_key (str): RongCloud application App Key.
            app_secret (str): RongCloud application App Secret.
            api_base (str, optional): Base URL of the API, default is China region.
            timeout (float, optional): Request timeout in seconds.

        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.api_base = api_base.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout, headers=DEFAULT_HEADERS)

    def _generate_nonce(self) -> str:
        """Generate a random nonce string."""
        return str(int(time.time() * 1000))

    def _generate_signature(self, nonce: str, timestamp: str) -> str:
        """Generate request signature."""
        sign_string = f'{self.app_secret}{nonce}{timestamp}'
        return hashlib.sha1(sign_string.encode('utf-8')).hexdigest()

    def _prepare_headers(self, headers: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Prepare request headers with authentication info."""
        nonce = self._generate_nonce()
        timestamp = str(int(time.time()))
        signature = self._generate_signature(nonce, timestamp)

        default_headers = {
            'App-Key': self.app_key,
            'Nonce': nonce,
            'Timestamp': timestamp,
            'Signature': signature,
        }

        if headers:
            default_headers.update(headers)

        return default_headers

    async def _parse_error_response(self, response: httpx.Response) -> APIErrorDetail:
        """Parse and normalize error responses."""
        try:
            error_data = response.json()
            return APIErrorDetail(
                code=error_data.get('code'),
                message=error_data.get('errorMessage') or error_data.get('message'),
                http_status=response.status_code,
            )
        except json.JSONDecodeError:
            return APIErrorDetail(
                code=response.status_code,
                message=response.text[:200],
                http_status=response.status_code,
            )

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        jsonParams: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute an HTTP request.

        Args:
            method (str): HTTP method ('GET', 'POST', etc.).
            endpoint (str): API endpoint path.
            data (Optional[Dict[str, Any]], optional): Form data for POST requests.
            params (Optional[Dict[str, Any]], optional): Query parameters for GET requests.
            jsonParams (Optional[Dict[str, Any]], optional): JSON payload for POST requests.
            headers (Optional[Dict[str, Any]], optional): Additional headers.

        Returns:
            Dict[str, Any]: Parsed JSON response.

        """
        url = f'{self.api_base}{endpoint}'
        headers = self._prepare_headers(headers)

        try:
            if method.upper() == 'GET':
                response = await self.client.get(url, headers=headers, params=params)
            else:
                response = await self.client.post(url, headers=headers, data=data, json=jsonParams)

            response.raise_for_status()

            result = response.json()

            if isinstance(result, dict):
                code = result.get('code')
                if code != 200:
                    error_detail = APIErrorDetail(
                        code=code,
                        message=result.get('message', 'Business error'),
                        http_status=200,
                    )
                    raise RongCloudAPIError(error_detail)

            return result

        except httpx.HTTPStatusError as e:
            error_detail = await self._parse_error_response(e.response)
            raise RongCloudAPIError(error_detail)

        except json.JSONDecodeError as e:
            error_detail = APIErrorDetail(
                code=500,
                message=f'Invalid JSON response: {str(e)}',
            )
            raise RongCloudAPIError(error_detail)

        except httpx.RequestError as e:
            raise RongCloudRequestError(str(e))

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
