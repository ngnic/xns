import uuid

from django.db import models


class CustomerCallback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_secret = models.UUIDField(
        null=False, blank=False, default=uuid.uuid4, editable=False
    )
    callback_url = models.URLField(null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["callback_url"],
                name="udx_callback_url",
                condition=models.Q(deleted_at__isnull=True),
            )
        ]


class CustomerMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_key = models.TextField(null=False, blank=False)
    amount = models.DecimalField(
        null=False, blank=False, decimal_places=4, max_digits=20
    )
    account_number = models.TextField(null=False, blank=False)
    bank_code = models.TextField(null=False, blank=False)
    currency = models.TextField(null=False, blank=False)
    transaction_occured_at = models.DateTimeField(
        null=False, blank=False, auto_now_add=True
    )
    system_attempts = models.IntegerField(null=False, blank=False, default=0)
    user_attempts = models.IntegerField(null=False, blank=False, default=0)
    callback = models.ForeignKey(
        "notifications.CustomerCallback",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    system_last_attempted_at = models.DateTimeField(null=True, blank=True)
    user_last_attempted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["external_key"],
                name="udx_external_key",
                condition=models.Q(deleted_at__isnull=True),
            )
        ]
