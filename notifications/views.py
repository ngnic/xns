from django.db.utils import IntegrityError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from notifications.models import CustomerCallback
from notifications.serializers import (CustomerCallbackSerializer,
                                       CustomerMessageSerializer)
from notifications.tasks import send_notification


class CustomerCallbackViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
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
