import os
import sys
import time
from dotenv import load_dotenv
from loguru import logger
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import Field
from rongcloud_server_mcp.sdk.client import RongCloudClient
from rongcloud_server_mcp.sdk.exceptions import RongCloudError
from rongcloud_server_mcp.sdk.services.message import HistoryMessage
from rongcloud_server_mcp.sdk.services.user import UserInfoResponse
from typing import List, Optional


# Load environment variables once at module level
load_dotenv()

# Set up logging
logger.remove()
# logger.add(sys.stderr, level=os.getenv('FASTMCP_LOG_LEVEL', 'WARNING'))
logger.add(sys.stderr, level=os.getenv('FASTMCP_LOG_LEVEL', 'INFO'))

# Initialize FastMCP server
mcp = FastMCP(
    'rongcloud-server-mcp-python',
    instructions="An MCP server implementation based on RongCloud IM Server.",
)

@mcp.tool(
    name='get_current_time_millis',
    description="Get the current time in milliseconds since Unix epoch (January 1, 1970 UTC).",
)
def get_current_time_millis()->int:
    """Get the current time in milliseconds since Unix epoch (January 1, 1970 UTC)."""
    return int(time.time() * 1000)


@mcp.tool(
    name='register_user',
    description="Register a new user via RongCloud and return the user's token.",
)
async def register_user(
        user_id: str = Field(
            description='User ID defined by the app to obtain a token. Supports a combination of uppercase and lowercase letters and numbers, with a maximum length of 64 bytes.'
        ),
        name: str = Field(
            description='User name used for push services. Supports any characters including symbols, English letters, and Chinese characters, limited to a maximum of 64 characters.'
        ),
        portrait_uri: str = Field('', description='User avatar URI, maximum length 1024 bytes.')
):
    """Register a new user via RongCloud and return the user's token."""

    async def call(client: RongCloudClient):
        token_result = await client.users.get_token(user_id, name, portrait_uri or '')
        return token_result

    return await execute_api_call('register_user', call)


@mcp.tool(name='get_user_info', description='Retrieve user information using RongCloud.')
async def get_user_info(
        user_id: str = Field(
            description='User ID defined by the app.'
        ),
) -> UserInfoResponse:
    """Retrieve user information using RongCloud."""

    async def call(client: RongCloudClient):
        user_info_result = await client.users.get_user_info(user_id)
        return user_info_result

    return await execute_api_call('get_user_info', call)


@mcp.tool(
    name='send_private_text_message',
    description='Send private text messages to one or multiple recipients via RongCloud.',
)
async def send_private_text_message(
        from_user_id: str = Field(description='Sender user ID.'),
        to_user_ids: list[str] = Field(
            description='Recipient user IDs. Supports sending to multiple users, up to 1000 per call.'
        ),
        content: str = Field(description='Message content. Max size: 128KB'),
) -> list[dict[str, str]]:
    """Send private text messages to one or multiple recipients via RongCloud."""
    async def call(client: RongCloudClient):
        txt_message = {'content': content}
        result = await client.messages.send_private(
            from_user_id=from_user_id,
            to_user_ids=to_user_ids,
            object_name='RC:TxtMsg',
            content=txt_message,
        )
        response_list = [
            {'user_id': entry.target_id, 'message_uid': entry.message_uid}
            for entry in result.message_uids
        ]
        return response_list

    return await execute_api_call('send_private_text_message', call)


@mcp.tool(
    name='send_group_text_message',
    description='Send group text messages to one or multiple groups via RongCloud.',
)
async def send_group_text_message(
        from_user_id: str = Field(description='Sender user ID.'),
        to_group_ids: List[str] = Field(
            description='Recipient group IDs. Supports up to 3 group IDs. When sending directed group messages, only one group ID is allowed.'
        ),
        content: str = Field(description='Message content. Max size: 128KB.'),
) -> list[dict[str, str]]:
    """Send group text messages to one or multiple groups via RongCloud."""

    async def call(client: RongCloudClient):
        txt_message = {'content': content}
        result = await client.messages.send_group_message(
            from_user_id=from_user_id,
            to_group_ids=to_group_ids,
            object_name='RC:TxtMsg',
            content=txt_message,
        )
        response_list = [
            {'group_id': entry.target_id, 'message_uid': entry.message_uid}
            for entry in result.message_uids
        ]
        return response_list

    return await execute_api_call('send_group_text_message', call)


@mcp.tool(
    name='get_private_messages',
    description='Retrieves historical private messages between two users within a specified time range.The time range is defined by startTime (newest) and endTime (oldest),with endTime must be earlier than startTime.',
)
async def get_private_messages(
        user_id: str = Field(description='ID of the user whose messages are being queried'),
        target_id: str = Field(description='ID of the other user in the private conversation'),
        end_time: Optional[int] = Field(None,
            description='End timestamp in milliseconds (default: 24 hours before end time)'),
        start_time: Optional[int] = Field(None,description='Start timestamp in milliseconds (must be later than endTime, default: current time)'),
        page_size: int = Field(50, description='Number of messages per page (default: 50, max: 100)'),
) -> list[HistoryMessage]:
    """Retrieves historical private messages between two users within a specified time range."""
    # Set default values if not provided
    current_millis = int(time.time() * 1000)
    start_time = start_time or current_millis
    end_time = end_time or (current_millis - 24 * 60 * 60 * 1000)

    page_size =  min(100, max(1, page_size))

    logger.info(f"get_private_messages {user_id}-{target_id}-{end_time}-{start_time}-{page_size}")

    async def call(client: RongCloudClient):
        result = await client.messages.get_private_messages(
            user_id=user_id,
            target_id=target_id,
            start_time=start_time,
            end_time=end_time,
            page_size=page_size,
            include_start=True,
        )
        return result

    return await execute_api_call('get_private_messages', call)


@mcp.tool(
    name='create_group',
    description='Creates a new group chat in RongCloud with specified members.',
)
async def create_group(
        user_ids: List[str] = Field(description='List of user IDs to join the group, max 1000 users.'),
        group_id: str = Field(description='Group ID, max length 64 characters. Supports letters and numbers.'),
        group_name: str = Field(description='Group name, max length 128 characters.'),
):
    """Creates a new group with the specified ID and members."""

    async def call(client: RongCloudClient):
        await client.groups.create_group(
            user_ids=user_ids, group_id=group_id, group_name=group_name
        )
        return f'Group created successfully: groupId={group_id}, groupName={group_name}, memberCount={len(user_ids)}'

    return await execute_api_call('create_group', call)


@mcp.tool(
    name='dismiss_group',
    description='Permanently deletes a group chat from RongCloud.',
)
async def dismiss_group(
        user_id: str = Field(description="Operator's user ID."),
        group_id: str = Field(description='Group ID'),
):
    """Permanently deletes a group chat from RongCloud."""

    async def call(client: RongCloudClient) -> str:
        await client.groups.dismiss_group(user_id=user_id, group_id=group_id)
        return f'Group dismissed successfully: groupId={group_id} by userId={user_id}'

    return await execute_api_call('dismiss_group', call)


@mcp.tool(
    name='get_group_members',
    description='Retrieves the complete member list of an existing group chat in RongCloud.',
)
async def get_group_members(
        group_id: str = Field(description='Group ID'),
) -> dict:
    """Retrieves the complete member list of an existing group chat in RongCloud."""

    async def call(client: RongCloudClient):
        group_members = await client.groups.get_group_members(
            group_id=group_id
        )
        return {'members': group_members}

    return await execute_api_call('get_group_members', call)

@mcp.tool(name='join_group', description='Adds one or more users to a specified group chat via RongCloud.')
async def join_group(
        user_ids: list[str] = Field(description='User IDs to add to the group. Up to 1000 users.'),
        group_id: str = Field(description='Group ID'),
        group_name: str = Field(default='', description='Group name'),
):
    """Adds specified users to a group."""

    async def call(client: RongCloudClient):
        await client.groups.join_group(user_ids=user_ids, group_id=group_id, group_name=group_name)
        return f"Successfully added {len(user_ids)} members to group '{group_name}' (groupId={group_id})"

    return await execute_api_call('join_group', call)


@mcp.tool(name='quit_group', description='Removes one or more users from a RongCloud group chat.')
async def quit_group(
        user_ids: List[str] = Field(description='User IDs to remove from the group. Up to 1000 users.'),
        group_id: str = Field(description='Group ID'),
):
    """Removes specified users from a group."""

    async def call(client: RongCloudClient):
        await client.groups.quit_group(user_ids=user_ids, group_id=group_id)
        return f'Successfully removed {len(user_ids)} members from group (groupId={group_id})'

    return await execute_api_call('quit_group', call)


async def execute_api_call(tool_name: str, func):
    """Generic helper function to handle RongCloud client lifecycle,
    invoke a provided asynchronous function with the client, and
    uniformly handle exceptions.
    """
    async with create_rongcloud_client() as client:
        try:
            return await func(client)
        except RongCloudError as error:
            logger.error(f'[{tool_name}] RongCloud api error: {str(error)}')
            raise ToolError(f'[{tool_name}] RongCloud api error: {str(error)}')
        except Exception as error:
            logger.exception(f'[{tool_name}] Unexpected error: {str(error)}')
            raise ToolError(f'[{tool_name}] Unexpected error: {str(error)}')


def create_rongcloud_client() -> RongCloudClient:
    """Creates and returns a configured RongCloud client instance.

    Required Environment Variables:
    - RONGCLOUD_APP_KEY: Application key (required)
    - RONGCLOUD_APP_SECRET: Application secret (required)

    Optional Environment Variables:
    - RONGCLOUD_API_BASE: API base URL (default: production endpoint)

    Returns:
        Initialized RongCloudClient instance

    Raises:
        ValueError: When required environment variables are missing
        RuntimeError: When client initialization fails

    """
    # Get configuration
    app_key = os.getenv('RONGCLOUD_APP_KEY')
    app_secret = os.getenv('RONGCLOUD_APP_SECRET')
    api_base = os.getenv('RONGCLOUD_API_BASE', 'https://api-cn.ronghub.com')
    api_timeout = int(os.getenv('RONGCLOUD_API_TIMEOUT', '10'))

    # Validate required configuration
    if not all([app_key, app_secret]):
        missing = []
        if not app_key:
            missing.append('RONGCLOUD_APP_KEY')
        if not app_secret:
            missing.append('RONGCLOUD_APP_SECRET')
        error_msg = f'Missing required environment variables: {", ".join(missing)}'
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        # Secure logging (partial app key display)
        logger.debug(f'Initializing RongCloud client, AppKey: {app_key},ApiBase: {api_base}')
        return RongCloudClient(
            app_key=app_key,
            app_secret=app_secret,
            api_base=api_base,
            api_timeout=api_timeout,
        )
    except Exception as e:
        logger.error(f'Client initialization failed: {str(e)}')
        raise RuntimeError(f'Client initialization failed: {str(e)}') from e


def main():
    """
    Entry point of the application that starts the FastMCP server.
    """
    logger.info('Using standard stdio transport')
    mcp.run()


if __name__ == '__main__':
    main()
