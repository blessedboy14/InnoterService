from jose import jwt

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from InnoterService import settings
from blog.utils import TempUserEntity

logger = settings.logger


class CustomJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        logger.info(
            f"Processing user request to protected resource, checking token: {token}"
        )
        if not token:
            logger.error("error with token processing: no token provided")
            raise AuthenticationFailed("No token provided")
        token = self._retrieve_raw_token(token)
        try:
            payload = self._decode_jwt(token)
        except jwt.JWTError as e:
            logger.error(
                f"error with token processing: expired token or incorrect payload, error: {e}"
            )
            raise AuthenticationFailed(f"Authentication error: {e}")
        user_entity = TempUserEntity(payload["user_id"], token)
        user_entity.authenticate()
        return user_entity, None

    @staticmethod
    def _retrieve_raw_token(token: str) -> str:
        return token[token.index(" ") + 1 :]

    @staticmethod
    def _decode_jwt(token: str) -> dict:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload