import pytest
from pydantic import ValidationError
from rongcloud_server_mcp.sdk.exceptions import APIErrorDetail, RongCloudAPIError
from rongcloud_server_mcp.sdk.services.user import (
    TokenResponse,
    UserInfoResponse,
    UserService,
)
from unittest.mock import AsyncMock


@pytest.fixture
def mock_client():
    """Returns an AsyncMock that has a .request(...) coroutine method.

    By default, .request() will return {} (an empty dict).
    Individual tests override mock_client.request.return_value or side_effect.
    """
    client = AsyncMock()
    client.request.return_value = {}
    return client


@pytest.mark.asyncio
async def test_get_token_success(mock_client):
    """If client.request returns {"token": "abc123"}.

    get_token(...) should return a TokenResponse(token="abc123").
    """
    svc = UserService(mock_client)
    expected = {'token': 'abc123'}
    mock_client.request.return_value = expected

    result: TokenResponse = await svc.get_token(
        user_id='user42', name='Alice', portrait_uri='http://avatar.example/1.png'
    )

    assert isinstance(result, TokenResponse)
    assert result.token == 'abc123'
    mock_client.request.assert_awaited_once_with(
        'POST',
        '/user/getToken.json',
        data={
            'userId': 'user42',
            'name': 'Alice',
            'portraitUri': 'http://avatar.example/1.png',
        },
    )


@pytest.mark.asyncio
async def test_get_token_without_portrait(mock_client):
    """If portrait_uri is None.

    The data payload should omit "portraitUri".
    """
    svc = UserService(mock_client)
    expected = {'token': 'no_pic_token'}
    mock_client.request.return_value = expected

    result = await svc.get_token(user_id='user99', name='Bob', portrait_uri=None)

    assert isinstance(result, TokenResponse)
    assert result.token == 'no_pic_token'
    mock_client.request.assert_awaited_once_with(
        'POST', '/user/getToken.json', data={'userId': 'user99', 'name': 'Bob'}
    )


@pytest.mark.asyncio
async def test_get_user_info_success(mock_client):
    """If client.request returns a dict with keys userName, userPortrait, createTime.

    get_user_info(...) should return a UserInfoResponse with the correct attributes.
    """
    svc = UserService(mock_client)
    raw = {
        'userName': 'Charlie',
        'userPortrait': 'http://portrait.example/charlie.png',
        'createTime': '2025-06-01T12:00:00Z',
    }
    mock_client.request.return_value = raw

    result: UserInfoResponse = await svc.get_user_info(user_id='charlieID')

    assert isinstance(result, UserInfoResponse)
    assert result.user_name == 'Charlie'
    assert result.user_portrait == 'http://portrait.example/charlie.png'
    assert result.create_time == '2025-06-01T12:00:00Z'

    mock_client.request.assert_awaited_once_with(
        'POST', '/user/info.json', data={'userId': 'charlieID'}
    )


@pytest.mark.asyncio
async def test_get_user_info_user_not_exist(mock_client):
    """If client.request raises RongCloudAPIError with error_detail.code == 400.

    get_user_info(...) must catch it and re‐raise a new RongCloudAPIError whose
    detail.code == 400 and message == "User does not exist".
    """
    svc = UserService(mock_client)
    original_detail = APIErrorDetail(code=400, message='Some raw 400 error', http_status=400)
    original_exc = RongCloudAPIError(original_detail)
    mock_client.request.side_effect = original_exc

    with pytest.raises(RongCloudAPIError) as exc_info:
        await svc.get_user_info(user_id='nonexistent')

    new_exc: RongCloudAPIError = exc_info.value
    assert isinstance(new_exc, RongCloudAPIError)
    assert new_exc.error_detail.code == 400
    assert new_exc.error_detail.message == 'User does not exist'
    assert new_exc.error_detail.http_status == 400

    mock_client.request.assert_awaited_once_with(
        'POST', '/user/info.json', data={'userId': 'nonexistent'}
    )


@pytest.mark.asyncio
async def test_get_user_info_other_error_re_raised(mock_client):
    """If client.request raises RongCloudAPIError with a code ≠ 400.

    get_user_info(...) should not catch it specially—it should bubble the original exception.
    """
    svc = UserService(mock_client)
    original_detail = APIErrorDetail(code=500, message='Internal server error', http_status=500)
    original_exc = RongCloudAPIError(original_detail)
    mock_client.request.side_effect = original_exc

    with pytest.raises(RongCloudAPIError) as exc_info:
        await svc.get_user_info(user_id='someID')

    assert exc_info.value is original_exc
    mock_client.request.assert_awaited_once_with(
        'POST', '/user/info.json', data={'userId': 'someID'}
    )


@pytest.mark.parametrize(
    'bad_payload,missing_field',
    [
        ({'userPortrait': 'p', 'createTime': 't'}, 'userName'),
        ({'userName': 'Eve', 'createTime': 't'}, 'userPortrait'),
        ({'userName': 'Eve', 'userPortrait': 'p'}, 'createTime'),
    ],
)
def test_user_info_response_validation_errors(bad_payload, missing_field):
    """If the returned dict is missing any required field (userName, userPortrait, createTime).

    Pydantic should raise ValidationError when constructing UserInfoResponse.
    """
    with pytest.raises(ValidationError) as exc_info:
        UserInfoResponse(**bad_payload)

    err_text = str(exc_info.value)
    assert missing_field in err_text


@pytest.mark.parametrize(
    'invalid_type_payload,wrong_field',
    [
        ({'userName': 123, 'userPortrait': 'p', 'createTime': 't'}, 'userName'),
        ({'userName': 'Eve', 'userPortrait': 456, 'createTime': 't'}, 'userPortrait'),
        ({'userName': 'Eve', 'userPortrait': 'p', 'createTime': 789}, 'createTime'),
    ],
)
def test_user_info_response_type_validation_errors(invalid_type_payload, wrong_field):
    """If any field has the wrong type (e.g. int instead of str).

    Pydantic should raise ValidationError.
    """
    with pytest.raises(ValidationError) as exc_info:
        UserInfoResponse(**invalid_type_payload)

    err_text = str(exc_info.value)
    assert wrong_field in err_text
