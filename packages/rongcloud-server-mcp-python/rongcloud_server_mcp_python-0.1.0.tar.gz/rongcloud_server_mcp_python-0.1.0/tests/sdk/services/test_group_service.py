# tests/sdk/test_group_service.py

import pytest
from rongcloud_server_mcp.sdk.base_client import BaseClient
from rongcloud_server_mcp.sdk.services.group import GroupService, GroupUser
from unittest.mock import AsyncMock


@pytest.fixture
def mock_client():
    """Returns an object with an AsyncMock 'request' method.

    We'll inject this into GroupService.
    """
    client = AsyncMock(spec=BaseClient)
    # Ensure client.request is an AsyncMock returning None by default
    client.request.return_value = None
    return client


@pytest.mark.asyncio
async def test_create_group_calls_client_request_once(mock_client):
    """create_group(...) should call client.request(
      "POST", "/group/create.json", data={...}
    ) exactly once with the correct payload.

    """
    service = GroupService(mock_client)
    user_ids = ['userA', 'userB', 'userC']
    group_id = 'group123'
    group_name = 'Cool Group'

    await service.create_group(user_ids, group_id, group_name)

    # Build the expected data payload
    expected_data = {
        'groupId': group_id,
        'groupName': group_name,
        'userId': ','.join(user_ids),
    }
    mock_client.request.assert_awaited_once_with('POST', '/group/create.json', data=expected_data)


@pytest.mark.asyncio
async def test_dismiss_group_calls_client_request_once(mock_client):
    """dismiss_group(...) should call client.request(
      "POST", "/group/dismiss.json", data={...}
    ) exactly once with the correct payload.

    """
    service = GroupService(mock_client)
    user_id = 'leader123'
    group_id = 'group123'

    await service.dismiss_group(user_id, group_id)

    expected_data = {
        'userId': user_id,
        'groupId': group_id,
    }
    mock_client.request.assert_awaited_once_with('POST', '/group/dismiss.json', data=expected_data)


@pytest.mark.asyncio
async def test_join_group_calls_client_request_once_no_group_name(mock_client):
    """If group_name is omitted (defaults to ""), join_group(...) should still include
    an empty string under 'group_name' and call client.request(...) correctly.

    """
    service = GroupService(mock_client)
    user_ids = ['userX', 'userY']
    group_id = 'groupXYZ'

    # Not passing group_name explicitly, so it uses the default ""
    await service.join_group(user_ids, group_id)

    expected_data = {
        'groupId': group_id,
        'userId': ','.join(user_ids),
        'group_name': '',  # default value
    }
    mock_client.request.assert_awaited_once_with('POST', '/group/join.json', data=expected_data)


@pytest.mark.asyncio
async def test_join_group_calls_client_request_once_with_group_name(mock_client):
    """If group_name is provided, join_group(...) should include it in the payload.

    """
    service = GroupService(mock_client)
    user_ids = ['userX', 'userY']
    group_id = 'groupXYZ'
    group_name = 'Gaming Buddies'

    await service.join_group(user_ids, group_id, group_name)

    expected_data = {
        'groupId': group_id,
        'userId': ','.join(user_ids),
        'group_name': group_name,
    }
    mock_client.request.assert_awaited_once_with('POST', '/group/join.json', data=expected_data)


@pytest.mark.asyncio
async def test_quit_group_calls_client_request_once(mock_client):
    """quit_group(...) should call client.request(
      "POST", "/group/quit.json", data={...}
    ) exactly once with the correct payload.

    """
    service = GroupService(mock_client)
    user_ids = ['user1', 'user2', 'user3']
    group_id = 'groupQuit'

    await service.quit_group(user_ids, group_id)

    expected_data = {
        'groupId': group_id,
        'userId': ','.join(user_ids),
    }
    mock_client.request.assert_awaited_once_with('POST', '/group/quit.json', data=expected_data)


@pytest.mark.asyncio
async def test_get_group_members_calls_client_request_once(mock_client):
    """get_group_members(...) should call client.request(
        "POST", "/group/user/query.json", data={...}
    ) exactly once with the correct payload.
    """
    group_id = "test_group_123"
    mock_response = {
        "users": [
            {"id": "user1"},
            {"id": "user2"}
        ]
    }

    mock_client.request.return_value = mock_response

    service = GroupService(mock_client)

    result = await service.get_group_members(group_id)

    expected_data = {'groupId': group_id}
    mock_client.request.assert_awaited_once_with(
        'POST',
        '/group/user/query.json',
        data=expected_data
    )

    assert len(result) == 2
    assert isinstance(result[0], GroupUser)
    assert result[0].id == "user1"
    assert result[1].id == "user2"
