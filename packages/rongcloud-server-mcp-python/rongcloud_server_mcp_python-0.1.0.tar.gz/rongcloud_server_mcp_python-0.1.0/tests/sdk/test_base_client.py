import json
import pytest
import time
from httpx import AsyncClient, ConnectError, MockTransport, Request, Response
from rongcloud_server_mcp.sdk.base_client import BaseClient
from rongcloud_server_mcp.sdk.exceptions import RongCloudAPIError, RongCloudRequestError
from unittest.mock import patch


@pytest.mark.asyncio
async def test_successful_post_request():
    """Test successful POST request returning HTTP 200 with code 200.

    Ensures that BaseClient.request() returns the JSON response unchanged when
    both HTTP and business code indicate success.
    """
    async def handler(request: Request):
        payload = {'code': 200, 'result': 'ok'}
        return Response(
            200,
            content=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
        )

    client = BaseClient('test_key', 'test_secret')
    client.client = AsyncClient(transport=MockTransport(handler), timeout=client.timeout)

    result = await client.request(
        method='POST',
        endpoint='/message/send',
        jsonParams={'content': 'hello'},
    )
    assert result == {'code': 200, 'result': 'ok'}
    await client.close()


@pytest.mark.asyncio
async def test_business_error_code_not_200():
    """Test request with HTTP 200 but non-200 business code.

    Verifies that BaseClient.request() raises RongCloudAPIError when the response
    contains a business error code (e.g., 500), even if HTTP status is 200.
    """
    async def handler(request: Request):
        payload = {'code': 500, 'message': 'Some business error'}
        return Response(
            200,
            content=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
        )

    client = BaseClient('test_key', 'test_secret')
    client.client = AsyncClient(transport=MockTransport(handler), timeout=client.timeout)

    with pytest.raises(RongCloudAPIError) as exc_info:
        await client.request('POST', '/message/send', jsonParams={'foo': 'bar'})

    err_str = str(exc_info.value)
    assert '500' in err_str
    assert 'Some business error' in err_str
    await client.close()


@pytest.mark.asyncio
async def test_http_status_error():
    """Test HTTP-level error status such as 403.

    Ensures that BaseClient.request() raises RongCloudAPIError when the HTTP status
    is not 200, and includes error details in the exception message.
    """
    async def handler(request: Request):
        payload = {'code': 403, 'errorMessage': 'Access denied'}
        return Response(
            403,
            content=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
        )

    client = BaseClient('test_key', 'test_secret')
    client.client = AsyncClient(transport=MockTransport(handler), timeout=client.timeout)

    with pytest.raises(RongCloudAPIError) as exc_info:
        await client.request('GET', '/user/info')

    err_str = str(exc_info.value)
    assert '403' in err_str
    assert 'Access denied' in err_str
    await client.close()


@pytest.mark.asyncio
async def test_invalid_json_response():
    """Test handling of non-JSON responses.

    Ensures that BaseClient.request() raises RongCloudAPIError when the response
    body is not valid JSON despite having a 200 HTTP status.
    """
    async def handler(request: Request):
        return Response(200, content=b'not-json', headers={'Content-Type': 'application/json'})

    client = BaseClient('test_key', 'test_secret')
    client.client = AsyncClient(transport=MockTransport(handler), timeout=client.timeout)

    with pytest.raises(RongCloudAPIError) as exc_info:
        await client.request('GET', '/message')

    err_str = str(exc_info.value)
    assert 'Invalid JSON' in err_str
    await client.close()


@pytest.mark.asyncio
async def test_request_exception():
    """Test behavior when request fails due to network issues.

    Ensures that ConnectError is caught and converted to RongCloudRequestError
    when the request cannot be sent.
    """
    async def handler(request: Request):
        raise ConnectError('Connection failure', request=request)

    client = BaseClient('test_key', 'test_secret')
    client.client = AsyncClient(transport=MockTransport(handler), timeout=client.timeout)

    with pytest.raises(RongCloudRequestError) as exc_info:
        await client.request('GET', '/anything')

    assert 'Connection failure' in str(exc_info.value)
    await client.close()


def test_signature_and_prepare_headers():
    """Test signature generation and custom header preparation.

    Ensures that nonce, timestamp, and signature are deterministic under patched time,
    and that custom headers are correctly merged with the default headers.
    """
    client = BaseClient('my_app_key', 'my_app_secret')

    with patch('time.time', return_value=1_600_000_000):
        nonce = client._generate_nonce()
        assert nonce == '1600000000000'

        timestamp = str(int(time.time()))
        assert timestamp == '1600000000'

        signature = client._generate_signature(nonce, timestamp)
        assert isinstance(signature, str)
        assert len(signature) == 40

        expected = client._generate_signature(nonce, timestamp)
        assert signature == expected

        custom_headers = {'X-Custom-Header': 'value123'}
        merged = client._prepare_headers(custom_headers)

        assert merged['App-Key'] == 'my_app_key'
        assert merged['Nonce'] == nonce
        assert merged['Timestamp'] == timestamp
        assert merged['Signature'] == signature
        assert merged['X-Custom-Header'] == 'value123'
