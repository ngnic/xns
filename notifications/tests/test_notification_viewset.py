from decimal import *

import pytest
from django.urls import reverse
from django.utils import timezone
from mixer.backend.django import mixer
from notifications.models import CustomerMessage
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_callback():
    return mixer.blend(
        "notifications.CustomerCallback", callback_url="https://test.com"
    )


@pytest.mark.django_db
class TestNotificationViewset:
    def test_retry_route(self, api_client, mocker, customer_callback):
        now = timezone.now()
        message = CustomerMessage(
            external_key="test",
            amount=Decimal("10.00"),
            bank_code="test_bank",
            account_number="123",
            currency="IDR",
            callback=customer_callback,
            transaction_occured_at=now,
        )
        message.save()
        mock_fn = mocker.patch("notifications.tasks.send_notification.apply_async")
        response = api_client.post(
            reverse(
                "notifications:customermessage-retry", kwargs={"pk": message.id.hex}
            )
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_fn.assert_called_with(
            kwargs={"message_id": message.id.hex, "manual_retry": True}
        )

    def test_retry_route_raises_error_if_message_doesnt_exist(self, api_client, mocker):
        now = timezone.now()
        mock_fn = mocker.patch("notifications.tasks.send_notification.apply_async")
        response = api_client.post(
            reverse("notifications:customermessage-retry", kwargs={"pk": "some_pk"})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_fn.assert_not_called()
