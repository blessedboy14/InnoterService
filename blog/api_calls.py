import enum
import requests


class RequestedDataType(enum.Enum):
    GROUP_ID = "group_id"
    ROLE = "role"


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


role_values = [a.value for a in UserRole]


def fetch_user_data(token: str, requested_type: RequestedDataType) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get("http://localhost:8080/users/me", headers=headers)
        if response.status_code != 200:
            return None
        return _parse_response_data(requested_type, response.json())
    except requests.ConnectionError as e:
        # TODO: logging here
        return None


def fetch_user_data_as_moderator(
    token: str, requested_type: RequestedDataType, user_id: str
) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"http://localhost:8080/users/{user_id}", headers=headers
        )
        if response.status_code != 200:
            return None
        return _parse_response_data(requested_type, response.json())
    except requests.ConnectionError as e:
        return None


def _parse_response_data(
    requested_type: RequestedDataType, response_data: dict
) -> dict | None:
    requested_data = response_data.get(requested_type.value, None)
    return requested_data
