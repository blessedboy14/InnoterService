import pytest
from rest_framework import status


@pytest.mark.django_db
def test_create_tag(api_client, get_fake_tag, get_auth_headers):
    response = api_client.post('/tag', headers=get_auth_headers, data=get_fake_tag)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == get_fake_tag['name']


@pytest.mark.django_db
def test_list_empty_tags(api_client, get_auth_headers):
    response = api_client.get('/tags', headers=get_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.django_db
def test_list_tags_with_filter(api_client, get_auth_headers, get_fake_tag):
    tag = get_fake_tag
    response = api_client.post('/tag', headers=get_auth_headers, data=tag)
    assert response.status_code == status.HTTP_201_CREATED
    tag_name = tag['name']
    response = api_client.get(
        f'/tags?filter_by_name={tag_name}', headers=get_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_create_then_list_tags(api_client, get_auth_headers, get_fake_tag):
    response = api_client.get('/tags', headers=get_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    response = api_client.post('/tag', headers=get_auth_headers, data=get_fake_tag)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == get_fake_tag['name']
    response = api_client.get('/tags', headers=get_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_create_duplicate_tag(api_client, get_auth_headers, get_fake_tag):
    response = api_client.post('/tag', headers=get_auth_headers, data=get_fake_tag)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == get_fake_tag['name']
    response = api_client.post('/tag', headers=get_auth_headers, data=get_fake_tag)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_authentication_barrier(api_client):
    response = api_client.get('/tags')
    assert response.status_code == status.HTTP_403_FORBIDDEN
