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
