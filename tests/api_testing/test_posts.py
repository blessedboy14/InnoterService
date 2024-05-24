import uuid

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_create_post(api_client, get_auth_headers, get_fake_post, create_fake_page):
    post = get_fake_post
    page_id = create_fake_page
    post.update({'page': page_id})
    response = api_client.post(f'/page/{page_id}/post', data=post, headers=get_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['content'] == post['content']


@pytest.mark.django_db
def test_create_post_on_nonexistent_page(api_client, get_auth_headers, get_fake_post):
    post = get_fake_post
    page_id = uuid.uuid4()
    post.update({'page': page_id})
    response = api_client.post(f'/page/{page_id}/post', data=post, headers=get_auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_and_delete_post(api_client, get_auth_headers, create_fake_post):
    post_id = create_fake_post
    response = api_client.delete(f'/post/{post_id}', headers=get_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = api_client.delete(f'/post/{post_id}', headers=get_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_post(api_client, get_auth_headers, create_fake_post):
    post_id = create_fake_post
    to_update = {'content': 'updated_content'}
    response = api_client.patch(f'/post/{post_id}', headers=get_auth_headers, data=to_update)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['content'] == to_update['content']
