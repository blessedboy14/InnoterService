import pytest


@pytest.mark.django_db
def test_read_feed(get_auth_headers, api_client):
    response = api_client.get("/feed", headers=get_auth_headers)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_page_without_tags_associated(get_auth_headers, api_client, get_fake_page):
    fake_page = get_fake_page
    response = api_client.post("/page", headers=get_auth_headers,
                               data=fake_page)
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_page_successfully(get_auth_headers, api_client, create_fake_tag, get_fake_page):
    fake_tag_id = create_fake_tag
    fake_page = get_fake_page
    fake_page.update({'tags': fake_tag_id})
    response = api_client.post("/page", headers=get_auth_headers, data=fake_page)
    assert response.status_code == 201
    assert response.json()['name'] == fake_page['name']


@pytest.mark.django_db
def test_create_page_duplicate_error(get_auth_headers, api_client, create_fake_tag, get_fake_page):
    fake_tag_id = create_fake_tag
    fake_page = get_fake_page
    fake_page.update({'tags': fake_tag_id})
    response = api_client.post("/page", headers=get_auth_headers, data=fake_page)
    assert response.status_code == 201
    assert response.json()['name'] == fake_page['name']
    response = api_client.post("/page", headers=get_auth_headers, data=fake_page)
    assert response.status_code == 400


@pytest.mark.django_db
def test_delete_page(get_auth_headers, api_client, create_fake_page):
    page_id = create_fake_page
    response = api_client.delete(f"/page/{page_id}", headers=get_auth_headers)
    assert response.status_code == 204
    response = api_client.delete(f"/page/{page_id}", headers=get_auth_headers)
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_nonexistent_page(get_auth_headers, api_client):
    response = api_client.delete("/page/<non-exist-id>", headers=get_auth_headers)
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_page(get_auth_headers, api_client, create_fake_page):
    page_id = create_fake_page
    response = api_client.get(f"/page/{page_id}?page=1&limit=2", headers=get_auth_headers)
    assert response.status_code == 200
    assert response.json()['id'] == page_id


@pytest.mark.django_db
def test_patch_page_name(get_auth_headers, api_client, create_admins_page):
    page_id = create_admins_page
    to_update = {'name': 'updated_name'}
    response = api_client.patch(f"/page/{page_id}", headers=get_auth_headers, data=to_update)
    assert response.status_code == 200
    assert response.json()['name'] == to_update['name']


@pytest.mark.django_db
def test_patch_replace_tags_on_page(get_auth_headers, api_client, create_admins_page, create_fake_tags):
    page_id = create_admins_page
    response = api_client.get(f"/page/{page_id}", headers=get_auth_headers)
    assert response.status_code == 200
    assert response.json()['id'] == page_id
    tags = create_fake_tags
    to_update = {'tags': [tags['tag1'], tags['tag2']]}
    response = api_client.patch(f"/page/{page_id}", headers=get_auth_headers, data=to_update)
    assert response.status_code == 200
    assert len(response.json()['tags']) == 2


@pytest.mark.django_db
def test_add_new_tags_to_page(get_auth_headers, api_client, create_admins_page, create_fake_tags):
    page_id = create_admins_page
    response = api_client.get(f"/page/{page_id}", headers=get_auth_headers)
    assert response.status_code == 200
    assert response.json()['id'] == page_id
    tags = create_fake_tags
    old_tag = response.json()['tags'][0]['id']
    to_update = {'tags': [tags['tag1'], tags['tag2'], old_tag]}
    response = api_client.patch(f"/page/{page_id}", headers=get_auth_headers, data=to_update)
    assert response.status_code == 200
    assert len(response.json()['tags']) == 3



