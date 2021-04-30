import uuid

from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from notifications.models import CustomerCallback, CustomerMessage
from notifications.serializers import (CustomerCallbackSerializer,
                                       CustomerMessageSerializer)
from notifications.tasks import send_notification


class CustomerCallbackViewset(
    mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = CustomerCallback.objects.filter(deleted_at__isnull=True)
    serializer_class = CustomerCallbackSerializer

    @action(detail=True, methods=["post"])
    def notifications(self, request, pk=None):
        self.serializer_class = CustomerMessageSerializer
        request.data["callback"] = pk
        try:
            response = super().create(request)
            if response.status_code == status.HTTP_201_CREATED:
                send_notification.apply_async(
                    kwargs={"message_id": response.data["id"]}
                )
            return response
        except IntegrityError as e:
            raise ValidationError({"error": str(e)})

    def destroy(self, request, pk=None):
        now = timezone.now()
        callback_id = uuid.UUID(pk)
        with transaction.atomic():
            CustomerCallback.objects.filter(
                id=callback_id, deleted_at__isnull=True
            ).update(deleted_at=now)
            CustomerMessage.objects.filter(
                callback_id=callback_id, deleted_at__isnull=True
            ).update(deleted_at=now)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationViewset(viewsets.GenericViewSet):
    queryset = CustomerMessage.objects.select_related("callback").filter(
        deleted_at__isnull=True
    )
    serializer_class = CustomerMessageSerializer

    @action(detail=True, methods=["post"])
    def retry(self, request, *args, **kwargs):
        instance = self.get_object()
        send_notification.apply_async(
            kwargs={"message_id": instance.id.hex, "manual_retry": True}
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
