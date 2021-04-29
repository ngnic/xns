import hashlib
import hmac
import uuid


def create_message_digest(key, message):
    key = uuid.UUID(key)
    return hmac.new(
        key.bytes, message.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()


def verify_message_digest(key, message, comparison_digest):
    hash_a = create_message_digest(key, message)
    return hash_a == comparison_digest
