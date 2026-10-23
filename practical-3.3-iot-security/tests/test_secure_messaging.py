import unittest

from scripts.secure_messaging import create_message, verify_message, seen_nonces


class SecureMessagingTests(unittest.TestCase):
    def setUp(self):
        seen_nonces.clear()

    def test_valid_message_is_accepted(self):
        message = create_message("sensor-01", 22.5)
        self.assertTrue(verify_message(message))

    def test_replayed_message_is_rejected(self):
        message = create_message("sensor-01", 22.5)
        self.assertTrue(verify_message(message))
        self.assertFalse(verify_message(message))

    def test_modified_message_is_rejected(self):
        message = create_message("sensor-01", 22.5)
        message["payload"]["temperature"] = 99.9
        self.assertFalse(verify_message(message))


if __name__ == "__main__":
    unittest.main()