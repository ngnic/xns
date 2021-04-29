from rest_framework import mixins, viewsets

from notifications.models import CustomerCallback
from notifications.serializers import CustomerCallbackSerializer


class CustomerCallbackViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CustomerCallback.objects.filter(deleted_at__isnull=True)
    serializer_class = CustomerCallbackSerializer
