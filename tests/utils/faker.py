import uuid

from faker import Faker

fake = Faker()


def fake_page(user_id: str | None = None) -> dict:
    if user_id is None:
        user_id = uuid.uuid4()
    return {
        "name": fake.name(),
        "description": fake.text(max_nb_chars=100),
        "user_id": user_id,
        "image_url": fake.image_url(),
    }


def fake_tag() -> dict:
    return {
        "name": fake.name(),
    }


def fake_post() -> dict:
    return {
        "content": fake.text(max_nb_chars=100),
    }
