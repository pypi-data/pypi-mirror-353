from .base_client import BaseClient
from .services import GroupService, MessageService, UserService


class RongCloudClient(BaseClient):
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        api_base: str,
        api_timeout: int = 10,
        **kwargs,
    ):
        super().__init__(app_key, app_secret, api_base, api_timeout, **kwargs)
        self.users = UserService(self)
        self.messages = MessageService(self)
        self.groups = GroupService(self)
