import pytest
import rongcloud_server_mcp.server as module  # Assuming the main file is server.py
import time
from mcp.server.fastmcp.exceptions import ToolError
from rongcloud_server_mcp.sdk.exceptions import RongCloudError
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    """Set required environment variables automatically before each test."""
    monkeypatch.setenv('RONGCLOUD_APP_KEY', 'test_key')
    monkeypatch.setenv('RONGCLOUD_APP_SECRET', 'test_secret')
    monkeypatch.setenv('FASTMCP_LOG_LEVEL', 'INFO')


@pytest.fixture
def mock_client_context():
    """Create a mock RongCloud client with async context support and method stubs.

    Returns:
        MagicMock: Mocked RongCloud client.
    """
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    mock_client.users = MagicMock()
    mock_client.users.get_token = AsyncMock()
    mock_client.users.get_user_info = AsyncMock()

    mock_client.messages = MagicMock()
    mock_client.messages.send_private = AsyncMock()
    mock_client.messages.send_group_message = AsyncMock()
    mock_client.messages.get_private_messages = AsyncMock()

    mock_client.groups = MagicMock()
    mock_client.groups.create_group = AsyncMock()
    mock_client.groups.dismiss_group = AsyncMock()
    mock_client.groups.join_group = AsyncMock()
    mock_client.groups.quit_group = AsyncMock()
    mock_client.groups.get_group_members = AsyncMock()

    return mock_client


@pytest.mark.asyncio
async def test_execute_api_call_success(mock_client_context):
    """Test successful execution of API call."""
    mock_func = AsyncMock(return_value='success')

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.execute_api_call('test_tool', mock_func)
        assert result == 'success'
        mock_func.assert_called_once_with(mock_client_context)


@pytest.mark.asyncio
async def test_execute_api_call_rongcloud_error(mock_client_context):
    """Test that RongCloudError is converted to ToolError."""
    mock_func = AsyncMock(side_effect=RongCloudError('API error'))

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        with pytest.raises(ToolError, match=r'RongCloud api error'):
            await module.execute_api_call('test_tool', mock_func)


@pytest.mark.asyncio
async def test_execute_api_call_unexpected_error(mock_client_context):
    """Test that unexpected exceptions are converted to ToolError."""
    mock_func = AsyncMock(side_effect=ValueError('Unexpected'))

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        with pytest.raises(ToolError, match=r'Unexpected error'):
            await module.execute_api_call('test_tool', mock_func)


def test_create_rongcloud_client_success(monkeypatch):
    """Test successful instantiation of RongCloud client."""
    client = module.create_rongcloud_client()
    assert client.app_key == 'test_key'
    assert client.app_secret == 'test_secret'
    assert client.api_base == 'https://api-cn.ronghub.com'


def test_create_rongcloud_client_missing_env(monkeypatch):
    """Test that missing environment variables raise ValueError."""
    monkeypatch.delenv('RONGCLOUD_APP_KEY')
    monkeypatch.delenv('RONGCLOUD_APP_SECRET')

    with pytest.raises(ValueError, match=r'Missing required environment variables'):
        module.create_rongcloud_client()


@pytest.mark.asyncio
async def test_register_user(mock_client_context):
    """Test user registration via RongCloud API."""
    mock_response = MagicMock()
    mock_response.token = 'test_token'
    mock_client_context.users.get_token.return_value = mock_response

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.register_user('user123', 'John Doe', 'avatar.jpg')
        assert result.token == 'test_token'
        mock_client_context.users.get_token.assert_called_once_with(
            'user123', 'John Doe', 'avatar.jpg'
        )


@pytest.mark.asyncio
async def test_get_user_info(mock_client_context):
    """Test retrieving user information."""
    mock_response = MagicMock()
    mock_response.user_id = 'user123'
    mock_client_context.users.get_user_info.return_value = mock_response

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.get_user_info('user123')
        assert result.user_id == 'user123'
        mock_client_context.users.get_user_info.assert_called_once_with('user123')


@pytest.mark.asyncio
async def test_send_private_text_message(mock_client_context):
    """Test sending a private text message."""
    mock_response = MagicMock()
    mock_entry = MagicMock()
    mock_entry.target_id = 'user456'
    mock_entry.message_uid = 'msg123'
    mock_response.message_uids = [mock_entry]
    mock_client_context.messages.send_private.return_value = mock_response

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.send_private_text_message('user123', ['user456'], 'Hello there!')
        assert result[0]['user_id'] == 'user456'
        assert result[0]['message_uid'] == 'msg123'
        mock_client_context.messages.send_private.assert_called_once_with(
            from_user_id='user123',
            to_user_ids=['user456'],
            object_name='RC:TxtMsg',
            content={'content': 'Hello there!'},
        )


@pytest.mark.asyncio
async def test_send_group_text_message(mock_client_context):
    """Test sending a group text message."""
    mock_response = MagicMock()
    mock_entry = MagicMock()
    mock_entry.target_id = 'group789'
    mock_entry.message_uid = 'msg456'
    mock_response.message_uids = [mock_entry]
    mock_client_context.messages.send_group_message.return_value = mock_response

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.send_group_text_message('user123', ['group789'], 'Group message')
        assert result[0]['group_id'] == 'group789'
        assert result[0]['message_uid'] == 'msg456'
        mock_client_context.messages.send_group_message.assert_called_once_with(
            from_user_id='user123',
            to_group_ids=['group789'],
            object_name='RC:TxtMsg',
            content={'content': 'Group message'},
        )




@pytest.mark.asyncio
async def test_get_private_messages(mock_client_context):
    """Test retrieving private message history."""
    mock_message = MagicMock()
    mock_message.content = 'Test message'
    mock_client_context.messages.get_private_messages.return_value = [mock_message]

    end_time = int(time.time() * 1000)
    start_time = end_time - 3600000  # 1 hour ago

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.get_private_messages(
            user_id='user123',
            target_id='user456',
            end_time=end_time,
            start_time=start_time,
            page_size=50,
        )
        assert result[0].content == 'Test message'
        mock_client_context.messages.get_private_messages.assert_called_once_with(
            user_id='user123',
            target_id='user456',
            start_time=start_time,
            end_time=end_time,
            page_size=50,
            include_start=True,
        )



@pytest.mark.asyncio
async def test_create_group(mock_client_context):
    """Test group creation functionality."""
    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.create_group(['user1', 'user2'], 'group123', 'Test Group')
        assert 'created successfully' in result
        mock_client_context.groups.create_group.assert_called_once_with(
            user_ids=['user1', 'user2'], group_id='group123', group_name='Test Group'
        )


@pytest.mark.asyncio
async def test_dismiss_group(mock_client_context):
    """Test dismissing a group."""
    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.dismiss_group('user123', 'group123')
        assert 'dismissed successfully' in result
        mock_client_context.groups.dismiss_group.assert_called_once_with(
            user_id='user123', group_id='group123'
        )



@pytest.mark.asyncio
async def test_get_group_members(mock_client_context):
    """Test retrieving group members."""
    mock_member = MagicMock()
    mock_member.id = "user1"
    mock_client_context.groups.get_group_members.return_value = [mock_member]

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.get_group_members(
            group_id='group123'
        )

        assert 'members' in result
        assert len(result['members']) == 1
        assert result['members'][0].id == 'user1'

        mock_client_context.groups.get_group_members.assert_called_once_with(
            group_id='group123'
        )
@pytest.mark.asyncio
async def test_join_group(mock_client_context):
    """Test adding users to a group."""
    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.join_group(['user1', 'user2'], 'group123', 'Test Group')
        assert 'added 2 members' in result
        mock_client_context.groups.join_group.assert_called_once_with(
            user_ids=['user1', 'user2'], group_id='group123', group_name='Test Group'
        )


@pytest.mark.asyncio
async def test_quit_group(mock_client_context):
    """Test removing users from a group."""
    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        result = await module.quit_group(['user123'], 'group123')
        assert 'removed 1 members' in result
        mock_client_context.groups.quit_group.assert_called_once_with(
            user_ids=['user123'], group_id='group123'
        )


@pytest.mark.asyncio
async def test_send_message_too_many_recipients(mock_client_context):
    """Test error handling when message exceeds max recipient limit."""
    mock_client_context.messages.send_private.side_effect = RongCloudError(
        'Too many recipients (max 1000)'
    )

    with patch.object(module, 'create_rongcloud_client', return_value=mock_client_context):
        to_user_ids = [f'user{i}' for i in range(1001)]

        with pytest.raises(ToolError, match=r'Too many recipients'):
            await module.send_private_text_message('user123', to_user_ids, 'Mass message')
