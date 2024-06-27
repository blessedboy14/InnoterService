import uuid

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_create_post(api_client, get_fake_post, create_fake_page, mock_authentication):
    post = get_fake_post
    page_id = create_fake_page
    post.update({'page': page_id})
    response = api_client.post(f'/page/{page_id}/post', data=post)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['content'] == post['content']


@pytest.mark.django_db
def test_create_post_on_nonexistent_page(
    api_client, get_fake_post, mock_authentication
):
    post = get_fake_post
    page_id = uuid.uuid4()
    post.update({'page': page_id})
    response = api_client.post(
        f'/page/{page_id}/post',
        data=post,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_and_delete_post(
    api_client, create_fake_post, monkeypatch, mock_authentication
):
    post_id = create_fake_post

    def mock_get_role(self, *args, **kwargs):
        return 'admin'

    monkeypatch.setattr('blog.utils.fetch_user_data', mock_get_role)

    response = api_client.delete(f'/post/{post_id}')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = api_client.delete(f'/post/{post_id}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_post(api_client, create_fake_post, monkeypatch, mock_authentication):
    post_id = create_fake_post

    def mock_get_role(self, *args, **kwargs):
        return 'admin'

    monkeypatch.setattr('blog.utils.fetch_user_data', mock_get_role)

    to_update = {'content': 'updated_content'}
    response = api_client.patch(f'/post/{post_id}', data=to_update)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['content'] == to_update['content']


@pytest.mark.django_db
def test_like_post(api_client, mock_authentication, create_fake_post):
    post_id = create_fake_post
    response = api_client.post(f'/post/{post_id}/like')
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_like_then_unlike_post(api_client, mock_authentication, create_fake_post):
    post_id = create_fake_post
    response = api_client.post(f'/post/{post_id}/like')
    assert response.status_code == status.HTTP_201_CREATED
    response = api_client.post(f'/post/{post_id}/like')
    assert response.status_code == status.HTTP_200_OK
