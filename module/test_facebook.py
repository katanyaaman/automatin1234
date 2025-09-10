import unittest
import os
from module.envfacebook import FacebookClient

class TestFacebookClient(unittest.TestCase):
    def setUp(self):
        os.environ['FB_PAGE_ID'] = 'test_page_id'
        os.environ['FB_ACCESS_TOKEN'] = 'test_token'
        self.client = FacebookClient()

    def test_load_access_token(self):
        self.assertIsNotNone(self.client.access_token, "Access token should be loaded")

    def test_send_message(self):
        # This would require mocking requests, but for simplicity, check if method runs without error
        try:
            self.client.send_message("test_recipient", "Test message")
        except Exception as e:
            self.fail(f"send_message raised an exception: {e}")

    def test_get_latest_message(self):
        # Similarly, mock or check for no error
        result = self.client.get_latest_message()
        # Add assertions based on expected behavior

if __name__ == '__main__':
    unittest.main()