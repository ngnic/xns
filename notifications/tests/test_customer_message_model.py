from decimal import *

import pytest
from django.db import IntegrityError
from django.utils import timezone
from freezegun import freeze_time
from mixer.backend.django import mixer
from notifications.models import CustomerMessage


@pytest.fixture
def customer_callback():
    return mixer.blend("notifications.CustomerCallback")


@pytest.mark.django_db
class TestCustomerMessageModel:
    def test_create(self, customer_callback):
        precision = Decimal("1.00")
        message = CustomerMessage(
            external_key="test",
            amount=Decimal("10.00").quantize(precision),
            bank_code="test_bank",
            account_number="123",
            currency="IDR",
            callback=customer_callback,
        )
        now = timezone.now()
        with freeze_time(now) as frozen_datetime:
            message.full_clean()
            message.save()

        assert message.amount == Decimal("10.00").quantize(precision)
        assert message.external_key == "test"
        assert message.bank_code == "test_bank"
        assert message.account_number == "123"
        assert message.currency == "IDR"
        assert message.system_attempts == 0
        assert message.user_attempts == 0
        assert message.system_last_attempted_at is None
        assert message.user_last_attempted_at is None
        assert message.callback_id == customer_callback.id
        assert message.transaction_occured_at == now
        assert message.created_at == now

    def test_create_raises_integrity_error_if_message_with_external_key_exists(
        self, customer_callback
    ):
        precision = Decimal("1.00")
        message = CustomerMessage(
            external_key="test",
            amount=Decimal("10.00").quantize(precision),
            bank_code="test_bank",
            account_number="123",
            currency="IDR",
            callback=customer_callback,
        )
        message.save()

        message.id = None
        with pytest.raises(IntegrityError):
            message.save()

    def test_create_does_not_raise_integrity_error_if_deleted_message_with_external_key_exists(
        self, customer_callback
    ):
        now = timezone.now()
        precision = Decimal("1.00")
        message = CustomerMessage(
            external_key="test",
            amount=Decimal("10.00").quantize(precision),
            bank_code="test_bank",
            account_number="123",
            currency="IDR",
            callback=customer_callback,
            deleted_at=now,
        )
        message.save()

        message.id = None
        now = timezone.now()
        with freeze_time(now) as frozen_datetime:
            message.save()

        assert message.amount == Decimal("10.00").quantize(precision)
        assert message.external_key == "test"
        assert message.bank_code == "test_bank"
        assert message.account_number == "123"
        assert message.currency == "IDR"
        assert message.system_attempts == 0
        assert message.user_attempts == 0
        assert message.system_last_attempted_at is None
        assert message.user_last_attempted_at is None
        assert message.callback_id == customer_callback.id
        assert message.transaction_occured_at == now
        assert message.created_at == now
