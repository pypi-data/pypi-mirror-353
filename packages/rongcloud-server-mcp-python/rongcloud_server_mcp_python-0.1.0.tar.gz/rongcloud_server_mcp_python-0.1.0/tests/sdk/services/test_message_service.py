import json
import pytest
from pydantic import ValidationError
from rongcloud_server_mcp.sdk.services.message import (
    HistoryMessage,
    MessageService,
    MessageUID,
    SendMessageResponse,
)
from typing import List
from unittest.mock import AsyncMock


@pytest.fixture
def mock_client():
    """Provide a mock client whose .request(...) is an AsyncMock returning a dict by default."""
    client = AsyncMock()
    # By default, let request(...) return an empty dict.
    client.request.return_value = {}
    return client


def test_parse_message_uids_empty():
    """If the input dict has no "messageUIDs" key or it's empty, _parse_message_uids should return an empty list."""
    svc = MessageService(client=None)
    assert svc._parse_message_uids({}) == []
    assert svc._parse_message_uids({'messageUIDs': []}) == []


def test_parse_message_uids_mixed_user_and_group():
    """_parse_message_uids should pick "userId" if present, otherwise "groupId"."""
    svc = MessageService(client=None)
    raw = {
        'messageUIDs': [
            {'userId': 'alice', 'messageUID': 'uid1'},
            {'groupId': 'g1', 'messageUID': 'uid2'},
            {'userId': 'bob', 'messageUID': 'uid3'},
        ]
    }
    parsed: List[MessageUID] = svc._parse_message_uids(raw)
    assert len(parsed) == 3

    # Check each MessageUID model
    assert parsed[0].target_id == 'alice'
    assert parsed[0].message_uid == 'uid1'

    assert parsed[1].target_id == 'g1'
    assert parsed[1].message_uid == 'uid2'

    assert parsed[2].target_id == 'bob'
    assert parsed[2].message_uid == 'uid3'


@pytest.mark.asyncio
async def test_send_private_minimum_fields(mock_client):
    """send_private(...) with only the required parameters (no push_content/push_data/count/kwargs).

    Should:
      1. Build the correct "data" dict (content should be JSON‐encoded),
      2. Call client.request("POST", "/message/private/publish.json", data=...),
      3. Return a SendMessageResponse whose .message_uids list matches what _parse_message_uids produced.
    """
    svc = MessageService(client=mock_client)
    from_user = 'userA'
    to_users = ['userB', 'userC']
    object_name = 'RC:TxtMsg'
    content_dict = {'text': 'hello'}

    # Prepare a fake response: one user Id and messageUID each
    fake_resp = {
        'messageUIDs': [
            {'userId': 'userB', 'messageUID': 'muid1'},
            {'userId': 'userC', 'messageUID': 'muid2'},
        ]
    }
    mock_client.request.return_value = fake_resp

    result: SendMessageResponse = await svc.send_private(
        from_user,
        to_users,
        object_name,
        content_dict,
    )

    # Verify client.request was awaited once with correct arguments:
    expected_data = {
        'fromUserId': from_user,
        'toUserId': ','.join(to_users),
        'objectName': object_name,
        'content': json.dumps(content_dict),
        'isPersisted': 1,
        'isIncludeSender': 0,
        'disablePush': 'false',
        'expansion': 'false',
    }
    mock_client.request.assert_awaited_once_with(
        'POST',
        '/message/private/publish.json',
        data=expected_data,
    )

    # Check that SendMessageResponse was constructed correctly
    assert isinstance(result, SendMessageResponse)
    assert len(result.message_uids) == 2
    assert result.message_uids[0].target_id == 'userB'
    assert result.message_uids[0].message_uid == 'muid1'
    assert result.message_uids[1].target_id == 'userC'
    assert result.message_uids[1].message_uid == 'muid2'


@pytest.mark.asyncio
async def test_send_private_with_all_optional_fields(mock_client):
    """send_private(...) with push_content, push_data, count, disable_push=True, expansion=True.

    And extra kwargs (e.g. "extraKey":"extraValue") should include all of them in the data payload.
    """
    svc = MessageService(client=mock_client)
    from_user = 'uX'
    to_users = ['uY']
    obj_name = 'RC:ImgMsg'
    content_dict = {'url': 'https://.../image.png'}
    push_content = 'New image!'
    push_data = '{"foo":"bar"}'
    cnt = 5
    extra_kwargs = {'foo': 'bar', 'flag': 42}

    fake_resp = {
        'messageUIDs': [
            {'userId': 'uY', 'messageUID': 'muid-img'},
        ]
    }
    mock_client.request.return_value = fake_resp

    result = await svc.send_private(
        from_user,
        to_users,
        obj_name,
        content_dict,
        push_content=push_content,
        push_data=push_data,
        count=cnt,
        is_persisted=0,
        is_include_sender=1,
        disable_push=True,
        expansion=True,
        **extra_kwargs,
    )

    expected_data = {
        'fromUserId': 'uX',
        'toUserId': 'uY',
        'objectName': 'RC:ImgMsg',
        'content': json.dumps(content_dict),
        'isPersisted': 0,
        'isIncludeSender': 1,
        'disablePush': 'true',
        'expansion': 'true',
        'pushContent': push_content,
        'pushData': push_data,
        'count': cnt,
        'foo': 'bar',
        'flag': 42,
    }
    mock_client.request.assert_awaited_once_with(
        'POST',
        '/message/private/publish.json',
        data=expected_data,
    )

    assert isinstance(result, SendMessageResponse)
    assert len(result.message_uids) == 1
    assert result.message_uids[0].target_id == 'uY'
    assert result.message_uids[0].message_uid == 'muid-img'


@pytest.mark.asyncio
async def test_send_group_message_minimum_fields(mock_client):
    """send_group_message(...) with only required parameters.

    Should:
    1. Build correct data dict (content JSON‐encoded),
    2. Call client.request("POST", "/message/group/publish.json", data=...),
    3. Return SendMessageResponse matching _parse_message_uids output.
    """
    svc = MessageService(client=mock_client)
    from_user = 'sender1'
    group_ids = ['grp1', 'grp2']
    obj_name = 'RC:TxtMsg'
    content_dict = {'text': 'group hello'}

    fake_resp = {
        'messageUIDs': [
            {'groupId': 'grp1', 'messageUID': 'gmsg1'},
            {'groupId': 'grp2', 'messageUID': 'gmsg2'},
        ]
    }
    mock_client.request.return_value = fake_resp

    result: SendMessageResponse = await svc.send_group_message(
        from_user,
        group_ids,
        content_dict,
        obj_name,
    )

    expected_data = {
        'fromUserId': 'sender1',
        'toGroupId': ','.join(group_ids),
        'content': json.dumps(content_dict),
        'objectName': obj_name,
        'isPersisted': 1,
        'isIncludeSender': 0,
        'isMentioned': 0,
    }
    mock_client.request.assert_awaited_once_with(
        'POST',
        '/message/group/publish.json',
        data=expected_data,
    )

    assert isinstance(result, SendMessageResponse)
    assert len(result.message_uids) == 2
    assert result.message_uids[0].target_id == 'grp1'
    assert result.message_uids[0].message_uid == 'gmsg1'
    assert result.message_uids[1].target_id == 'grp2'
    assert result.message_uids[1].message_uid == 'gmsg2'


@pytest.mark.asyncio
async def test_send_group_message_with_all_optional_fields(mock_client):
    """send_group_message(...) with push_content, push_data, is_persisted=0, is_include_sender=1.

    is_mentioned=1, plus extra kwargs should appear in the data payload.
    """
    svc = MessageService(client=mock_client)
    from_user = 'senderX'
    group_ids = ['G1']
    obj_name = 'RC:CustomMsg'
    content_dict = {'key': 'value'}
    push_content = 'Notif!'
    push_data = '{"a":1}'
    extra_kw = {'foo': 'bar'}

    fake_resp = {
        'messageUIDs': [
            {'groupId': 'G1', 'messageUID': 'uidG1'},
        ]
    }
    mock_client.request.return_value = fake_resp

    result = await svc.send_group_message(
        from_user,
        group_ids,
        content_dict,
        obj_name,
        push_content=push_content,
        push_data=push_data,
        is_persisted=0,
        is_include_sender=1,
        is_mentioned=1,
        **extra_kw,
    )

    expected_data = {
        'fromUserId': 'senderX',
        'toGroupId': 'G1',
        'content': json.dumps(content_dict),
        'objectName': obj_name,
        'pushContent': push_content,
        'pushData': push_data,
        'isPersisted': 0,
        'isIncludeSender': 1,
        'isMentioned': 1,
        'foo': 'bar',
    }
    mock_client.request.assert_awaited_once_with(
        'POST',
        '/message/group/publish.json',
        data=expected_data,
    )

    assert isinstance(result, SendMessageResponse)
    assert len(result.message_uids) == 1
    assert result.message_uids[0].target_id == 'G1'
    assert result.message_uids[0].message_uid == 'uidG1'


@pytest.mark.asyncio
async def test_get_private_messages_happy_path(mock_client):
    """get_private_messages(...) should do the following.

    1. Call client.request("POST", "/v3/message/private/query.json", jsonParams=...),
    2. Parse the returned "data" list into HistoryMessage models.
    """
    svc = MessageService(client=mock_client)
    from_user = 'alice'
    to_user = 'bob'

    fake_response = {
        "data": [
            {
                "messageUID": "m1",
                "conversationType": 1,
                "targetId": "bob",
                "objectName": "RC:TxtMsg",
                "content": "{\"text\":\"hi\"}",
                "fromUserId": "alice",
                "msgTime": 123456789,
            },
            {
                "messageUID": "m2",
                "conversationType": 1,
                "targetId": "bob",
                "objectName": "RC:TxtMsg",
                "content": "{\"text\":\"hello again\"}",
                "fromUserId": "alice",
                "msgTime": 123456790,
            },
        ]
    }
    mock_client.request.return_value = fake_response

    messages: List[HistoryMessage] = await svc.get_private_messages(
        from_user,
        to_user,
        123456000,
        123457000,
        page_size=10,
    )

    mock_client.request.assert_awaited_once_with(
        'POST',
        '/v3/message/private/query.json',
        jsonParams={
            'userId': from_user,
            'targetId': to_user,
            'startTime': 123456000,
            'endTime': 123457000,
            'pageSize': 10,
            'includeStart': True,
        },
    )

    assert len(messages) == 2
    assert all(isinstance(m, HistoryMessage) for m in messages)
    assert messages[0].message_uid == 'm1'
    assert messages[1].message_uid == 'm2'


@pytest.mark.asyncio
async def test_get_private_messages_empty_and_missing_data_key(mock_client):
    """If the response dict has no "data" key or it's empty.

    get_private_messages(...) should return an empty list.
    """
    svc = MessageService(client=mock_client)

    # Case 1: No "data" key
    mock_client.request.return_value = {}
    result1 = await svc.get_private_messages('a', 'b', 'RC:TxtMsg', 5)
    assert result1 == []

    # Case 2: "data" key present but empty list
    mock_client.request.return_value = {"data": []}
    result2 = await svc.get_private_messages('a', 'b', 'RC:TxtMsg', 5)
    assert result2 == []


def test_history_message_validation_errors():
    """If a HistoryMessage dict is missing required fields or has wrong types.

    Pydantic should raise a ValidationError.
    """
    # Missing required fields
    incomplete_data = {
        "messageId": "m1",
        "conversationType": 1,
        # "targetId" missing
        "objectName": "RC:TxtMsg",
        "content": "{\"text\":\"hi\"}",
        "senderUserId": "alice",
        "sentTime": 123456789,
    }

    with pytest.raises(ValidationError):
        HistoryMessage(**incomplete_data)

    # Wrong type: sentTime should be int, but given string
    wrong_type_data = {
        "messageId": "m2",
        "conversationType": 1,
        "targetId": "bob",
        "objectName": "RC:TxtMsg",
        "content": "{\"text\":\"hi\"}",
        "senderUserId": "alice",
        "sentTime": "not-a-timestamp",
    }

    with pytest.raises(ValidationError):
        HistoryMessage(**wrong_type_data)
