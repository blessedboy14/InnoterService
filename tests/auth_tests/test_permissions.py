import uuid
from uuid import UUID

from mock import MagicMock

from blog.api_calls import UserRole, RequestedDataType
from blog.permissions import (
    IsCreator,
    IsAdminModerCreatorOrReadOnly,
    IsAdminOrGroupModerator,
)
from blog.utils import TempUserEntity


def test_is_creator_permission_true(get_admin_user_id):
    user_id = UUID(get_admin_user_id)
    page = MagicMock(user_id=user_id)
    request = MagicMock(custom_user=TempUserEntity(user_id=get_admin_user_id, token=''))
    assert IsCreator().has_object_permission(request, MagicMock(), page)


def test_is_creator_false(get_admin_user_id):
    user_id = uuid.uuid4()
    page = MagicMock(user_id=user_id)
    request = MagicMock(custom_user=TempUserEntity(user_id=get_admin_user_id, token=''))
    assert not IsCreator().has_object_permission(request, MagicMock(), page)


def test_is_admin_or_group_moderator_as_admin(get_admin_user_id, monkeypatch):
    def mock_fetch_user_data(*args, **kwargs):
        return 'admin'

    monkeypatch.setattr('blog.utils.fetch_user_data', mock_fetch_user_data)

    request = MagicMock(
        custom_user=TempUserEntity(
            user_id=get_admin_user_id, token='', role=UserRole.ADMIN
        )
    )
    assert IsAdminOrGroupModerator().has_object_permission(
        request, MagicMock(), MagicMock()
    )


def test_is_admin_or_group_moderator_as_group_moderator(get_admin_user_id, monkeypatch):
    group_id = uuid.uuid4()

    def mock_fetch_user_data(*args, **kwargs):
        if args[1] == RequestedDataType.ROLE:
            return 'moderator'
        else:
            return str(group_id)

    monkeypatch.setattr('blog.utils.fetch_user_data', mock_fetch_user_data)

    request = MagicMock(
        custom_user=TempUserEntity(
            user_id=get_admin_user_id,
            token='',
            role=UserRole.ADMIN,
            group_id=str(group_id),
        )
    )
    assert IsAdminOrGroupModerator().has_object_permission(
        request, MagicMock(), MagicMock()
    )


def test_is_admin_or_group_moderator_as_user(monkeypatch):
    def mock_fetch_user_data(*args, **kwargs):
        return 'user'

    monkeypatch.setattr('blog.utils.fetch_user_data', mock_fetch_user_data)

    request = MagicMock(custom_user=TempUserEntity(user_id=str(uuid.uuid4()), token=''))
    assert not IsAdminOrGroupModerator().has_object_permission(
        request, MagicMock(), MagicMock()
    )


def test_is_admin_moder_creator_as_creator(get_admin_user_id):
    user_id = UUID(get_admin_user_id)
    page = MagicMock(user_id=user_id)
    request = MagicMock(custom_user=TempUserEntity(user_id=get_admin_user_id, token=''))
    assert IsAdminModerCreatorOrReadOnly().has_object_permission(
        request, MagicMock(), page
    )


def test_is_admin_moder_creator_as_admin(get_admin_user_id, monkeypatch):
    def mock_fetch_user_data(*args, **kwargs):
        return 'admin'

    monkeypatch.setattr('blog.utils.fetch_user_data', mock_fetch_user_data)

    request = MagicMock(
        custom_user=TempUserEntity(
            user_id=get_admin_user_id, token='', role=UserRole.ADMIN
        )
    )
    assert IsAdminModerCreatorOrReadOnly().has_object_permission(
        request, MagicMock(), MagicMock()
    )


def test_is_admin_moder_creator_as_moderator(get_admin_user_id, monkeypatch):
    group_id = uuid.uuid4()

    def mock_fetch_user_data(*args, **kwargs):
        if args[1] == RequestedDataType.ROLE:
            return 'moderator'
        else:
            return str(group_id)

    monkeypatch.setattr('blog.utils.fetch_user_data', mock_fetch_user_data)

    request = MagicMock(
        custom_user=TempUserEntity(
            user_id=get_admin_user_id,
            token='',
            role=UserRole.ADMIN,
            group_id=str(group_id),
        )
    )
    assert IsAdminModerCreatorOrReadOnly().has_object_permission(
        request, MagicMock(), MagicMock()
    )


def test_is_admin_moder_creator_as_anonym(get_admin_user_id, monkeypatch):
    def mock_fetch_user_data(*args, **kwargs):
        return 'user'

    monkeypatch.setattr('blog.utils.fetch_user_data', mock_fetch_user_data)
    user_id = uuid.uuid4()
    page = MagicMock(user_id=user_id)
    request = MagicMock(custom_user=TempUserEntity(user_id=get_admin_user_id, token=''))
    assert not IsAdminModerCreatorOrReadOnly().has_object_permission(
        request, MagicMock(), page
    )
