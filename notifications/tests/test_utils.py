import uuid

from notifications.utils import create_message_digest, verify_message_digest


class TestHmacUtilities:
    def test_message_digest(self):
        key = uuid.uuid4().hex
        hash_a = create_message_digest(key, "quick brown fox")
        assert verify_message_digest(key, "quick brown fox", hash_a)
