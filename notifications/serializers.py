from rest_framework import serializers

from notifications.models import CustomerCallback


class CustomerCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCallback
        fields = ["id", "callback_url", "client_secret"]
        read_only_fields = ["id", "client_secret"]
        extra_kwargs = {
            "callback_url": {"write_only": True},
        }
