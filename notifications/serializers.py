from rest_framework import serializers

from notifications.models import CustomerCallback, CustomerMessage


class CustomerCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCallback
        fields = ["id", "callback_url", "client_secret"]
        read_only_fields = ["id", "client_secret"]
        extra_kwargs = {
            "callback_url": {"write_only": True},
        }


class CustomerMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerMessage
        fields = [
            "id",
            "external_key",
            "amount",
            "account_number",
            "bank_code",
            "currency",
            "transaction_occured_at",
            "callback",
        ]
        read_only_fields = ["id", "transaction_occured_at"]
