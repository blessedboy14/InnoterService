import pytest
from rest_framework import status


@pytest.mark.django_db
def test_create_tag(api_client, get_fake_tag, mock_authentication):
    response = api_client.post('/tag', data=get_fake_tag)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == get_fake_tag['name']


@pytest.mark.django_db
def test_list_empty_tags(api_client, mock_authentication):
    response = api_client.get('/tags')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['tags']) == 0


@pytest.mark.django_db
def test_list_tags_with_filter(api_client, mock_authentication, get_fake_tag):
    tag = get_fake_tag
    response = api_client.post('/tag', data=tag)
    assert response.status_code == status.HTTP_201_CREATED
    tag_name = tag['name']
    response = api_client.get(
        f'/tags?filter_by_name={tag_name}',
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['tags']) == 1


@pytest.mark.django_db
def test_create_then_list_tags(api_client, mock_authentication, get_fake_tag):
    response = api_client.get('/tags')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['tags']) == 0
    response = api_client.post('/tag', data=get_fake_tag)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == get_fake_tag['name']
    response = api_client.get(
        '/tags',
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['tags']) == 1


@pytest.mark.django_db
def test_create_duplicate_tag(api_client, mock_authentication, get_fake_tag):
    response = api_client.post('/tag', data=get_fake_tag)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == get_fake_tag['name']
    response = api_client.post('/tag', data=get_fake_tag)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
