import pytest
import os
from dotenv import load_dotenv, find_dotenv
from rest_framework import status
from rest_framework.test import APIClient
from tests.utils.faker import fake_page, fake_tag, fake_post


result = find_dotenv('tests/.env.test')
load_dotenv(result)


endless_token = os.getenv('ENDLESS_TOKEN', None)
admin_user_id = os.getenv('ADMIN_USER_ID', None)


@pytest.fixture
def api_client() -> APIClient:
    yield APIClient()


@pytest.fixture
def get_auth_headers() -> dict:
    return {'Authorization': f'Bearer {endless_token}'}


@pytest.fixture
def get_admin_user_id() -> str:
    return admin_user_id


@pytest.fixture
def get_fake_page() -> dict:
    return fake_page()


@pytest.fixture
def create_fake_tag(get_auth_headers, api_client) -> dict:
    tag = fake_tag()
    response = api_client.post('/tag', data=tag, headers=get_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()['id']


@pytest.fixture
def create_fake_tags(get_auth_headers, api_client) -> dict:
    tag1 = fake_tag()
    tag2 = fake_tag()
    tags = {}
    response = api_client.post('/tag', data=tag1, headers=get_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    tags.update({'tag1': response.json()['id']})
    response = api_client.post('/tag', data=tag2, headers=get_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    tags.update({'tag2': response.json()['id']})
    return tags


@pytest.fixture
def get_fake_post() -> dict:
    return fake_post()


@pytest.fixture
def create_fake_post(get_auth_headers, api_client, get_fake_post, create_fake_page):
    page_id = create_fake_page
    post = get_fake_post
    post.update({'page': page_id})
    response = api_client.post(f'/page/{page_id}/post', data=post, headers=get_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()['id']


@pytest.fixture
def create_admins_post(api_client, create_admins_page, get_fake_post, get_auth_headers):
    page_id = create_admins_page
    post = get_fake_post
    post.update({'page': page_id})
    response = api_client.post(f'/page/{page_id}/post', data=post, headers=get_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()['id']


@pytest.fixture
def get_fake_tag() -> dict:
    return fake_tag()


@pytest.fixture
def get_admins_page(get_admin_user_id) -> dict:
    return fake_page(get_admin_user_id)


@pytest.fixture
def get_correct_page_dict(create_fake_tag, get_fake_page) -> dict:
    fake_tag_id = create_fake_tag
    page = get_fake_page
    page.update({'tags': fake_tag_id})
    return page


@pytest.fixture
def create_fake_page(api_client, get_correct_page_dict, get_auth_headers) -> str:
    page = get_correct_page_dict
    response = api_client.post("/page", headers=get_auth_headers, data=page)
    assert response.status_code == 201
    assert response.json()['name'] == page['name']
    return response.json()['id']


@pytest.fixture
def create_admins_page(api_client, get_admins_page, create_fake_tag, get_auth_headers) -> str:
    tag_id = create_fake_tag
    page = get_admins_page
    page.update({'tags': tag_id})
    response = api_client.post("/page", headers=get_auth_headers, data=page)
    assert response.status_code == 201
    return response.json()['id']
