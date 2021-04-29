import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCustomerCallbackViewset:
    def test_create_route(self, api_client):
        request_body = {"callback_url": "https://test.com"}
        response = api_client.post(
            reverse(
                "notifications:customercallback-list",
            ),
            request_body,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert "client_secret" in response.data

    def test_create_route_raises_error_if_callback_url_isnt_valid(self, api_client):
        request_body = {"callback_url": "some_url"}
        response = api_client.post(
            reverse(
                "notifications:customercallback-list",
            ),
            request_body,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response.render()
        assert (
            response.content.decode("utf-8")
            == '{"callback_url":["Enter a valid URL."]}'
        )
