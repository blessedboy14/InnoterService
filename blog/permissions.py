from rest_framework import permissions
from InnoterService import settings
from blog.api_calls import UserRole
from blog.models import Page

logger = settings.logger


class IsAdminModerCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        logger.info(
            f"checking IsAdminModerCreator permission to resource from user with id: {request.user.user_id}"
        )
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.get_role() or obj.user_id.hex == request.user.user_id:
            if not hasattr(obj, "user_id"):
                obj = Page.objects.get(pk=obj.page_id)
            bool_val = (
                obj.user_id.hex == request.user.user_id
                or request.user.role == UserRole.ADMIN.value
                or (
                    request.user.role == UserRole.MODERATOR.value
                    and request.user.get_group_id()
                    == request.user.try_get_another_user_group_id(obj.user_id)
                )
            )
            logger.info(
                f"permission checked for user id: {request.user.user_id}, with result: {bool_val}"
            )
            return bool_val
        logger.error(
            f"api call failed, when checking permission for user id: {request.user.user_id}"
        )
        return False


class IsCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        logger.info(
            f"checking IsCreator permission to resource from user with id: {request.user.user_id}"
        )
        return obj.user_id.hex == request.user.user_id


class IsAdminOrGroupModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        logger.info(
            f"checking AdminOrGroupModerator permission to resource from user with id: {request.user.user_id}"
        )
        if request.user.get_role():
            bool_val = request.user.role == UserRole.ADMIN.value or (
                request.user.role == UserRole.MODERATOR.value
                and request.user.get_group_id()
                == request.user.try_get_another_user_group_id(obj.user_id)
            )
            logger.info(
                f"permission checked for user id: {request.user.user_id}, with result: {bool_val}"
            )
            return bool_val
        logger.error(
            f"api call failed, when checking permission for user id: {request.user.user_id}"
        )
        return False
