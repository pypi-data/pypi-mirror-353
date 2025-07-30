import json
from pydantic import BaseModel, Field, TypeAdapter
from typing import Dict, List, Optional


class MessageUID(BaseModel):
    target_id: str
    message_uid: str


class SendMessageResponse(BaseModel):
    message_uids: List[MessageUID]


class HistoryMessage(BaseModel):
    target_id: str = Field(alias='targetId')
    from_user_id: str = Field(alias='fromUserId')
    message_uid: str = Field(alias='messageUID')
    msg_time: int = Field(alias='msgTime')
    object_name: str = Field(alias='objectName')
    content: str = Field(alias='content')
    expansion: Optional[bool] = Field(default=False, alias='expansion')
    extra_content: Optional[str] = Field(default=None, alias='extraContent')


class MessageService:
    def __init__(self, client):
        self._client = client

    def _parse_message_uids(self, resp: dict) -> List[MessageUID]:
        """Parse messageUIDs from response dict to list of MessageUID models."""
        return [
            MessageUID(
                target_id=item.get('userId') or item.get('groupId'),
                message_uid=item['messageUID'],
            )
            for item in resp.get('messageUIDs', [])
        ]

    async def send_private(
        self,
        from_user_id: str,
        to_user_ids: list[str],
        object_name: str,
        content: Dict,
        push_content: Optional[str] = None,
        push_data: Optional[str] = None,
        count: Optional[int] = None,
        is_persisted: int = 1,
        is_include_sender: int = 0,
        disable_push: bool = False,
        expansion: bool = False,
        **kwargs,
    ) -> SendMessageResponse:
        """Send a private message to one or multiple users.

        Args:
            from_user_id (str): Sender user ID.
            to_user_ids (list[str]): Single or list of recipient user IDs.
            object_name (str): Message type, e.g. "RC:TxtMsg".
            content (Dict): Message content as a dictionary.
            push_content (Optional[str], optional): Push notification content. Defaults to None.
            push_data (Optional[str], optional): Push notification data (JSON string). Defaults to None.
            count (Optional[int], optional): Optional count parameter. Defaults to None.
            is_persisted (int, optional): Whether message is persisted (1 or 0). Defaults to 1.
            is_include_sender (int, optional): Whether sender receives the message (1 or 0). Defaults to 0.
            disable_push (bool, optional): Disable push notification if True. Defaults to False.
            expansion (bool, optional): Expansion flag for message. Defaults to False.
            **kwargs: Additional parameters for the API.

        Returns:
            SendMessageResponse: Response containing message UIDs.

        """
        data = {
            'fromUserId': from_user_id,
            'toUserId': ','.join(to_user_ids),
            'objectName': object_name,
            'content': json.dumps(content),
            'isPersisted': is_persisted,
            'isIncludeSender': is_include_sender,
            'disablePush': str(disable_push).lower(),
            'expansion': str(expansion).lower(),
            **kwargs,
        }
        if push_content is not None:
            data['pushContent'] = push_content
        if push_data is not None:
            data['pushData'] = push_data
        if count is not None:
            data['count'] = count

        resp = await self._client.request('POST', '/message/private/publish.json', data=data)
        message_uids = self._parse_message_uids(resp)
        return SendMessageResponse(message_uids=message_uids)

    async def send_group_message(
        self,
        from_user_id: str,
        to_group_ids: list[str],
        content: Dict,
        object_name: str,
        push_content: Optional[str] = None,
        push_data: Optional[str] = None,
        is_persisted: int = 1,
        is_include_sender: int = 0,
        is_mentioned: int = 0,
        **kwargs,
    ) -> SendMessageResponse:
        """Send a message to a group, optionally with @mentions.

        Args:
            from_user_id (str): Sender user ID.
            to_group_ids (list[str]): Target group ID list.
            content (Dict): Message content as a dictionary.
            object_name (str): Message type, e.g. "RC:TxtMsg".
            push_content (Optional[str], optional): Push notification content. Defaults to None.
            push_data (Optional[str], optional): Push notification data (JSON string). Defaults to None.
            is_persisted (int, optional): Whether message is persisted (1 or 0). Defaults to 1.
            is_include_sender (int, optional): Whether sender receives the message (1 or 0). Defaults to 0.
            is_mentioned (int, optional): Whether message contains @mentions (1 or 0). Defaults to 0.
            **kwargs: Additional parameters for the API.

        Returns:
            SendMessageResponse: Response containing message UIDs.

        """
        data = {
            'fromUserId': from_user_id,
            'toGroupId': ','.join(to_group_ids),
            'content': json.dumps(content),
            'objectName': object_name,
            'isPersisted': is_persisted,
            'isIncludeSender': is_include_sender,
            'isMentioned': is_mentioned,
            **kwargs,
        }
        if push_content is not None:
            data['pushContent'] = push_content
        if push_data is not None:
            data['pushData'] = push_data

        resp = await self._client.request('POST', '/message/group/publish.json', data=data)
        message_uids = self._parse_message_uids(resp)
        return SendMessageResponse(message_uids=message_uids)

    async def get_private_messages(
        self,
        user_id: str,
        target_id: str,
        start_time: int,
        end_time: int,
        page_size: int = 50,
        include_start: bool = True,
        **kwargs,
    ) -> List[HistoryMessage]:
        """Query private chat history messages.

        Args:
            user_id (str): ID of the sender.
            target_id (str): ID of the conversation target.
            start_time (int): Start time (in milliseconds since epoch).
            end_time (int): End time (in milliseconds since epoch).
            page_size (int, optional): Number of messages per page. Defaults to 50.
            include_start (bool, optional): Whether to include the start time message. Defaults to True.
            **kwargs: Additional fields to pass to the API.

        Returns:
            List[HistoryMessage]: A list of historical messages.

        """
        data = {
            'userId': user_id,
            'targetId': target_id,
            'startTime': start_time,
            'endTime': end_time,
            'pageSize': page_size,
            'includeStart': include_start,
            **kwargs,
        }

        resp = await self._client.request(
            'POST', '/v3/message/private/query.json', jsonParams=data
        )
        message_list = resp.get('data', [])
        adapter = TypeAdapter(List[HistoryMessage])
        return adapter.validate_python(message_list)
