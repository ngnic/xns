import pytest
from django.core import exceptions
from django.db import IntegrityError
from django.utils import timezone
from freezegun import freeze_time
from notifications.models import CustomerCallback


@pytest.mark.django_db
class TestCustomerCallbackModel:
    def test_create(self):
        test_url = "https://test.com"
        customer_callback = CustomerCallback(callback_url=test_url)

        now = timezone.now()
        with freeze_time(now) as frozen_datetime:
            customer_callback.save()

        assert customer_callback.callback_url == test_url
        assert customer_callback.client_secret is not None
        assert customer_callback.deleted_at is None
        assert customer_callback.created_at == now

    def test_create_raises_error_if_callback_url_is_invalid(self):
        test_url = "something wrong"
        customer_callback = CustomerCallback()
        customer_callback.callback_url = test_url

        with pytest.raises(exceptions.ValidationError):
            customer_callback.full_clean()

    def test_create_raises_integrity_error_if_callback_url_is_registered(self):
        test_url = "https://test.com"
        customer_callback = CustomerCallback(callback_url=test_url)
        customer_callback.save()

        customer_callback.id = None
        with pytest.raises(IntegrityError):
            customer_callback.save()

    def test_create_does_not_raises_integrity_error_if_deleted_callback_exists(self):
        test_url = "https://test.com"
        customer_callback = CustomerCallback(
            callback_url=test_url, deleted_at=timezone.now()
        )
        customer_callback.save()

        customer_callback.id = None
        customer_callback.deleted_at = None
        now = timezone.now()
        with freeze_time(now) as frozen_datetime:
            customer_callback.save()
        assert customer_callback.callback_url == test_url
        assert customer_callback.client_secret is not None
        assert customer_callback.deleted_at is None
        assert customer_callback.created_at == now
