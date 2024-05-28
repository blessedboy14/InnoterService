import enum
import requests
from InnoterService import settings

logger = settings.logger


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
        logger.info(f"Performing API call to Users Service for {requested_type.value}")
        response = requests.get("http://localhost:8080/users/me", headers=headers)
        if response.status_code != 200:
            logger.error(
                f"Can't get info from Users API, status code: {response.status_code}"
            )
            return None
        return _parse_response_data(requested_type, response.json())
    except requests.ConnectionError as e:
        logger.error(f"Can't access users servers, may be offline, error: {e}")
        return None


def fetch_user_data_as_moderator(
    token: str, requested_type: RequestedDataType, user_id: str
) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}
    try:
        logger.info(
            f"Performing API call to Users Service as moderator to get another user data"
            f" of type: {requested_type.value}"
        )
        response = requests.get(
            f"http://localhost:8080/users/{user_id}", headers=headers
        )
        if response.status_code != 200:
            logger.error(
                f"Can't get info from Users API, status code: {response.status_code}"
            )
            return None
        return _parse_response_data(requested_type, response.json())
    except requests.ConnectionError as e:
        logger.error(f"Can't access users servers, may be offline, error: {e}")
        return None


def _parse_response_data(
    requested_type: RequestedDataType, response_data: dict
) -> dict | None:
    requested_data = response_data.get(requested_type.value, None)
    return requested_data
