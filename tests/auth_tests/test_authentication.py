from blog.authentication import CustomJWTAuthentication
from rest_framework.request import Request
from rest_framework.exceptions import AuthenticationFailed
from django.http import HttpRequest
import pytest


def test_correct_credentials(get_token):
    django_request = HttpRequest()
    django_request.META.setdefault("HTTP_AUTHORIZATION", "Bearer " + get_token)
    request = Request(request=django_request)
    try:
        CustomJWTAuthentication().authenticate(request)
        assert True
    except AuthenticationFailed as e:
        pytest.fail(e)


def test_no_token_provided(get_token):
    django_request = HttpRequest()
    request = Request(request=django_request)
    try:
        CustomJWTAuthentication().authenticate(request)
        assert False
    except AuthenticationFailed:
        assert True
    except Exception as e:
        pytest.fail(e)


def test_bad_token_provided(get_token):
    django_request = HttpRequest()
    django_request.META.setdefault(
        "HTTP_AUTHORIZATION", "Bearer " + "ewkere<not_a_token>"
    )
    request = Request(request=django_request)
    try:
        CustomJWTAuthentication().authenticate(request)
        assert False
    except AuthenticationFailed:
        assert True
    except Exception as e:
        pytest.fail(e)
