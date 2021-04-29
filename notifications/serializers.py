from notifications.models import CustomerCallback
from rest_framework import serializers


class CustomerCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCallback
        fields = ["id", "client_secret"]
