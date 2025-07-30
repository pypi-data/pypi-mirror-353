from ..exceptions import APIErrorDetail, RongCloudAPIError
from pydantic import BaseModel, Field, TypeAdapter
from typing import Optional


class TokenResponse(BaseModel):
    token: str


class UserInfoResponse(BaseModel):
    user_name: str = Field(alias='userName')
    user_portrait: str = Field(alias='userPortrait')
    create_time: str = Field(alias='createTime')


class UserService:
    def __init__(self, client):
        self._client = client

    async def get_token(
        self, user_id: str, name: str, portrait_uri: Optional[str] = None
    ) -> TokenResponse:
        """Get a user token.

        :param user_id: Unique user ID
        :param name: User's display name
        :param portrait_uri: (Optional) URI of the user's avatar
        :return: TokenResponse containing the token
        """
        data = {'userId': user_id, 'name': name}
        if portrait_uri:
            data['portraitUri'] = portrait_uri

        resp = await self._client.request('POST', '/user/getToken.json', data=data)
        return TokenResponse(**resp)

    async def get_user_info(self, user_id: str) -> UserInfoResponse:
        """Get user info.

        :param user_id: Unique user ID
        :return: UserInfoResponse containing user details
        """
        data = {'userId': user_id}


        try:
            resp = await self._client.request('POST', '/user/info.json', data=data)
            adapter = TypeAdapter(UserInfoResponse)
            return adapter.validate_python(resp)
        except RongCloudAPIError as error:
            if error.error_detail.code == 400:
                raise RongCloudAPIError(APIErrorDetail(400, 'User does not exist', 400))
            raise error
