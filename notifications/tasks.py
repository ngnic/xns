import json
import math
import uuid

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from requests.exceptions import RequestException

from notifications.models import CustomerMessage
from notifications.serializers import CustomerMessageSerializer
from notifications.utils import create_message_digest


@shared_task
def send_notification(message_id, manual_retry=False):
    message = CustomerMessage.objects.select_related("callback").get(
        id=uuid.UUID(message_id)
    )
    serializer = CustomerMessageSerializer(message)
    serialized_message = json.dumps(serializer.data)

    now = timezone.now()
    try:
        req = requests.post(
            message.callback.callback_url,
            data=serialized_message,
            headers={
                "Content-Type": "application/json",
                "X-MESSAGE-DIGEST": create_message_digest(
                    message.callback.client_secret.hex, serialized_message
                ),
            },
            timeout=settings.NOTIFICATION_TIMEOUT,
        )
        if not manual_retry:
            message.system_attempts += 1
            message.system_last_attempted_at = now
        else:
            message.user_attempts += 1
            message.user_last_attempted_at = now
        req.raise_for_status()
    except RequestException as e:
        next_attempt = message.system_attempts + 1
        if not manual_retry and next_attempt < settings.MAX_RETRY_ATTEMPTS:
            send_notification.apply_async(
                kwargs={"message_id": message_id},
                countdown=math.pow(2, next_attempt) * 60,
            )
    else:
        message.received_at = timezone.now()
    message.save()
