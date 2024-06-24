from jose import jwt
from rest_framework.exceptions import AuthenticationFailed

from InnoterService import settings
from InnoterService.settings import logger
from blog.authentication import CustomJWTAuthentication


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _verify_jwt_token(self, token: str):
        pass

    def __call__(self, request):
        try:
            user_entity, _ = CustomJWTAuthentication().authenticate(request)
        except AuthenticationFailed as e:
            logger.error(e)
            response = self.get_response(request)
            return response
        request.custom_user = user_entity
        response = self.get_response(request)
        return response

    @staticmethod
    def _retrieve_raw_token(token: str) -> str:
        return token[token.index(' ') + 1 :]

    @staticmethod
    def _decode_jwt(token: str) -> dict:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
