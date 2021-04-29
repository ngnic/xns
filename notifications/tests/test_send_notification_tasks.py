import json
import math
from decimal import *

import pytest
import responses
from django.conf import settings
from django.utils import timezone
from freezegun import freeze_time
from mixer.backend.django import mixer
from notifications.models import CustomerMessage
from notifications.tasks import send_notification
from notifications.utils import verify_message_digest
from rest_framework import status


@pytest.fixture
def customer_callback():
    return mixer.blend(
        "notifications.CustomerCallback", callback_url="https://test.com"
    )


@pytest.mark.django_db
class TestSendNotificationTask:
    @responses.activate
    def test_send(self, customer_callback):
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

        def request_callback(request):
            request_body = json.loads(request.body)
            assert (
                verify_message_digest(
                    customer_callback.client_secret.hex,
                    request.body,
                    request.headers["X-MESSAGE-DIGEST"],
                )
                is True
            )
            assert request_body["external_key"] == message.external_key
            assert request_body["bank_code"] == message.bank_code
            assert request_body["amount"] == str(
                message.amount.quantize(Decimal("1.0000"))
            )
            assert request_body["account_number"] == message.account_number
            assert request_body["currency"] == message.currency
            assert request_body[
                "transaction_occured_at"
            ] == message.transaction_occured_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            return (status.HTTP_200_OK, {}, None)

        responses.add_callback(
            responses.POST,
            customer_callback.callback_url,
            callback=request_callback,
            content_type="application/json",
        )

        now = timezone.now()
        with freeze_time(now):
            send_notification(message_id=message.id.hex)

        retrieved_message = CustomerMessage.objects.get(id=message.id)
        assert retrieved_message.system_attempts == 1
        assert retrieved_message.user_attempts == 0
        assert retrieved_message.user_last_attempted_at is None
        assert (
            retrieved_message.transaction_occured_at == message.transaction_occured_at
        )
        assert retrieved_message.system_last_attempted_at == now
        assert retrieved_message.received_at == now

    @responses.activate
    def test_send_retry_on_failure(self, customer_callback, mocker):
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

        def request_callback(request):
            request_body = json.loads(request.body)
            assert (
                verify_message_digest(
                    customer_callback.client_secret.hex,
                    request.body,
                    request.headers["X-MESSAGE-DIGEST"],
                )
                is True
            )
            assert request_body["external_key"] == message.external_key
            assert request_body["bank_code"] == message.bank_code
            assert request_body["amount"] == str(
                message.amount.quantize(Decimal("1.0000"))
            )
            assert request_body["account_number"] == message.account_number
            assert request_body["currency"] == message.currency
            assert request_body[
                "transaction_occured_at"
            ] == message.transaction_occured_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            return (status.HTTP_400_BAD_REQUEST, {}, None)

        responses.add_callback(
            responses.POST,
            customer_callback.callback_url,
            callback=request_callback,
            content_type="application/json",
        )
        mock_fn = mocker.patch("notifications.tasks.send_notification.apply_async")

        for attempt_index in range(1, settings.MAX_RETRY_ATTEMPTS - 1):
            now = timezone.now()
            with freeze_time(now):
                send_notification(message_id=message.id.hex)

            retrieved_message = CustomerMessage.objects.get(id=message.id)
            assert retrieved_message.system_attempts == attempt_index
            assert retrieved_message.user_attempts == 0
            assert retrieved_message.user_last_attempted_at is None
            assert retrieved_message.system_last_attempted_at == now
            assert retrieved_message.received_at is None

            mock_fn.assert_called_with(
                kwargs={"message_id": message.id.hex},
                countdown=math.pow(2, attempt_index + 1),
            )

    @responses.activate
    def test_send_manual_retry(self, customer_callback):
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

        def request_callback(request):
            request_body = json.loads(request.body)
            assert (
                verify_message_digest(
                    customer_callback.client_secret.hex,
                    request.body,
                    request.headers["X-MESSAGE-DIGEST"],
                )
                is True
            )
            assert request_body["external_key"] == message.external_key
            assert request_body["bank_code"] == message.bank_code
            assert request_body["amount"] == str(
                message.amount.quantize(Decimal("1.0000"))
            )
            assert request_body["account_number"] == message.account_number
            assert request_body["currency"] == message.currency
            assert request_body[
                "transaction_occured_at"
            ] == message.transaction_occured_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            return (status.HTTP_200_OK, {}, None)

        responses.add_callback(
            responses.POST,
            customer_callback.callback_url,
            callback=request_callback,
            content_type="application/json",
        )

        now = timezone.now()
        with freeze_time(now):
            send_notification(message_id=message.id.hex, manual_retry=True)

        retrieved_message = CustomerMessage.objects.get(id=message.id)
        assert retrieved_message.system_attempts == message.system_attempts
        assert retrieved_message.user_attempts == 1
        assert retrieved_message.user_last_attempted_at == now
        assert retrieved_message.system_last_attempted_at is None
        assert retrieved_message.received_at == now

    @responses.activate
    def test_send_manual_retry_failure(self, customer_callback):
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

        def request_callback(request):
            request_body = json.loads(request.body)
            assert (
                verify_message_digest(
                    customer_callback.client_secret.hex,
                    request.body,
                    request.headers["X-MESSAGE-DIGEST"],
                )
                is True
            )
            assert request_body["external_key"] == message.external_key
            assert request_body["bank_code"] == message.bank_code
            assert request_body["amount"] == str(
                message.amount.quantize(Decimal("1.0000"))
            )
            assert request_body["account_number"] == message.account_number
            assert request_body["currency"] == message.currency
            assert request_body[
                "transaction_occured_at"
            ] == message.transaction_occured_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            return (status.HTTP_400_BAD_REQUEST, {}, None)

        responses.add_callback(
            responses.POST,
            customer_callback.callback_url,
            callback=request_callback,
            content_type="application/json",
        )

        now = timezone.now()
        with freeze_time(now):
            send_notification(message_id=message.id.hex, manual_retry=True)

        retrieved_message = CustomerMessage.objects.get(id=message.id)
        assert retrieved_message.system_attempts == message.system_attempts
        assert retrieved_message.user_attempts == 1
        assert retrieved_message.user_last_attempted_at == now
        assert retrieved_message.system_last_attempted_at is None
        assert retrieved_message.received_at is None
