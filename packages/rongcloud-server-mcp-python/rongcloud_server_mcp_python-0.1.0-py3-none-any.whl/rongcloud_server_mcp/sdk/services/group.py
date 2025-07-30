from pydantic import BaseModel, Field, TypeAdapter
from typing import List


class GroupUser(BaseModel):
    id: str = Field(alias='id')


class GroupService:
    def __init__(self, client):
        self._client = client

    async def create_group(self, user_ids: list[str], group_id: str, group_name: str):
        """Create a group.

        :param user_ids: List of user IDs to be added to the group
        :param group_id: Unique group ID
        :param group_name: Name of the group
        :return: None
        """
        data = {
            'groupId': group_id,
            'groupName': group_name,
            'userId': ','.join(user_ids),
        }

        await self._client.request('POST', '/group/create.json', data=data)

    async def dismiss_group(self, user_id: str, group_id: str):
        """Dismiss a group.

        :param user_id: The ID of the user performing the dismissal
        :param group_id: The ID of the group to be dismissed
        :return: None
        """
        data = {'userId': user_id, 'groupId': group_id}

        await self._client.request('POST', '/group/dismiss.json', data=data)

    async def join_group(self, user_ids: list[str], group_id: str, group_name: str = ''):
        """Add users to a group.

        :param user_ids: List of user IDs to join the group
        :param group_id: Group ID
        :param group_name: Group name
        :return: None
        """
        data = {
            'groupId': group_id,
            'userId': ','.join(user_ids),
            'group_name': group_name,
        }
        await self._client.request('POST', '/group/join.json', data=data)

    async def quit_group(self, user_ids: list[str], group_id: str):
        """Remove users from a group.

        :param user_ids: List of user IDs to be removed from the group
        :param group_id: ID of the group to quit
        :return: None
        """
        data = {
            'groupId': group_id,
            'userId': ','.join(user_ids),
        }

        await self._client.request('POST', '/group/quit.json', data=data)

    async def get_group_members(self, group_id: str) -> List[GroupUser]:
        """Retrieve the list of members in a specified group.

        :param group_id: ID of the group to query for members
        :return: List of group member objects
        """
        data = {
            'groupId': group_id,
        }

        resp = await self._client.request('POST', '/group/user/query.json', data=data)
        user_list = resp.get('users', [])
        adapter = TypeAdapter(List[GroupUser])
        return adapter.validate_python(user_list)
