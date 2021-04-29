import pytest
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from mixer.backend.django import mixer
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

    def test_create_notification_route(self, api_client):
        request_body = {
            "external_key": "some_key",
            "amount": "1.00",
            "account_number": "ABC",
            "bank_code": "ABC",
            "currency": "SGD",
        }
        customer_callback = mixer.blend("notifications.CustomerCallback")

        now = timezone.now()
        with freeze_time(now) as frozen_datetime:
            response = api_client.post(
                reverse(
                    "notifications:customercallback-notifications",
                    kwargs={"pk": customer_callback.id},
                ),
                request_body,
                format="json",
            )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert response.data["external_key"] == request_body["external_key"]
        assert response.data["amount"] == "1.0000"
        assert response.data["account_number"] == request_body["account_number"]
        assert response.data["bank_code"] == request_body["bank_code"]
        assert response.data["currency"] == request_body["currency"]
        assert response.data["transaction_occured_at"] == now.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

    def test_create_notification_route_returns_error_if_external_key_is_duplciated(
        self, api_client
    ):
        request_body = {
            "external_key": "some_key",
            "amount": "1.00",
            "account_number": "ABC",
            "bank_code": "ABC",
            "currency": "SGD",
        }
        customer_callback = mixer.blend("notifications.CustomerCallback")

        now = timezone.now()
        with freeze_time(now) as frozen_datetime:
            response = api_client.post(
                reverse(
                    "notifications:customercallback-notifications",
                    kwargs={"pk": customer_callback.id},
                ),
                request_body,
                format="json",
            )
        assert response.status_code == status.HTTP_201_CREATED

        with freeze_time(now) as frozen_datetime:
            response = api_client.post(
                reverse(
                    "notifications:customercallback-notifications",
                    kwargs={"pk": customer_callback.id},
                ),
                request_body,
                format="json",
            )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
