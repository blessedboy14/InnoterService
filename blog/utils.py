from dataclasses import dataclass
from .api_calls import (
    UserRole,
    fetch_user_data,
    RequestedDataType,
    fetch_user_data_as_moderator,
    role_values,
)


@dataclass
class TempUserEntity:
    user_id: str
    token: str
    is_authenticated: bool = False
    group_id: str | None = None
    role: UserRole = UserRole.USER

    def authenticate(self):
        self.is_authenticated = True

    def get_role(self):
        fetched_role = fetch_user_data(self.token, RequestedDataType.ROLE)
        self.role = UserRole.USER.value if fetched_role is None else fetched_role
        return False if fetched_role is None else True

    def get_group_id(self):
        group_id = fetch_user_data(self.token, RequestedDataType.GROUP_ID)
        self.group_id = group_id

    def try_get_another_user_group_id(self, user_id: str):
        group_id = fetch_user_data_as_moderator(
            self.token, RequestedDataType.GROUP_ID, user_id
        )
        return group_id
