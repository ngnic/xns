from rest_framework import mixins, viewsets
from rest_framework.decorators import action

from notifications.models import CustomerCallback
from notifications.serializers import (CustomerCallbackSerializer,
                                       CustomerMessageSerializer)


class CustomerCallbackViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CustomerCallback.objects.filter(deleted_at__isnull=True)
    serializer_class = CustomerCallbackSerializer

    @action(detail=True, methods=["post"])
    def notifications(self, request, pk=None):
        self.serializer_class = CustomerMessageSerializer
        request.data["callback"] = pk
        return super().create(request)
