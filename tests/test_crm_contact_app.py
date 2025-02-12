import unittest
from unittest.mock import patch, MagicMock
from pages.crm_contact_app import insert_contact

class TestCRMContactApp(unittest.TestCase):
    @patch('sqlite3.connect')
    def setUp(self, mock_connect):
        # Create a mock connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        mock_connect.return_value = self.mock_conn

    def test_contact_insertion_invalid_email(self):
        """Test contact insertion with an invalid email address (should not call execute)"""
        # Using an invalid email for testing (to trigger early return)
        result = insert_contact(
            "Mr.", "Male", "John Doe",
            "invalid-email", "1234567890",
            "Test message", "123 Street",
            "Sydney", "2000", "New South Wales",
            "Australia"
        )

        # Assert that execute was not called since email is invalid
        self.mock_cursor.execute.assert_not_called()

        # Ensure the function returned False as the insertion didn't happen
        self.assertFalse(result)

    def tearDown(self):
        if hasattr(self, 'mock_conn'):
            self.mock_conn.close()

if __name__ == '__main__':
    unittest.main()
