import unittest
from unittest.mock import patch, MagicMock
from pages.crm_contact_app import insert_contact

class TestCRMContactApp(unittest.TestCase):

    def setUp(self):
        """Set up a mock database for testing purposes."""
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor

    def test_contact_insertion_valid(self):
        """Test contact insertion with a valid email address (should call execute)"""
        result = insert_contact(
            "Mr.", "Male", "John Doe",
            "john@example.com", "1234567890",
            "Test message", "123 Street",
            "Sydney", "2000", "New South Wales",
            "Australia"
        )
        
        self.mock_cursor.execute.assert_called_once()
        self.assertTrue(result)
        self.mock_conn.commit.assert_called_once()

    def test_contact_insertion_empty_name(self):
        """Test contact insertion with an empty name (should return False)"""
        result = insert_contact(
            "Mr.", "Male", "",  # Empty name
            "john@example.com", "1234567890",
            "Test message", "123 Street",
            "Sydney", "2000", "New South Wales",
            "Australia"
        )
        self.mock_cursor.execute.assert_not_called()
        self.assertTrue(result)

    def test_contact_insertion_invalid_email_format(self):
        """Test contact insertion with invalid email format (should not call execute)"""
        result = insert_contact(
            "Mr.", "Male", "John Doe",
            "invalid-email", "1234567890",
            "Test message", "123 Street",
            "Sydney", "2000", "New South Wales",
            "Australia"
        )
        self.mock_cursor.execute.assert_not_called()
        self.assertFalse(result)

    def test_contact_insertion_invalid_phone_number(self):
        """Test contact insertion with an invalid phone number (should not call execute)"""
        result = insert_contact(
            "Mr.", "Male", "John Doe",
            "john@example.com", "invalid-phone",
            "Test message", "123 Street",
            "Sydney", "2000", "New South Wales",
            "Australia"
        )
        self.mock_cursor.execute.assert_not_called()
        self.assertTrue(result)

    def test_contact_insertion_missing_country(self):
        """Test contact insertion missing country (should still insert with empty country)"""
        result = insert_contact(
            "Mr.", "Male", "John Doe",
            "john@example.com", "1234567890",
            "Test message", "123 Street",
            "Sydney", "2000", "New South Wales",
            ""  # Empty country value
        )
        self.mock_cursor.execute.assert_called_once()
        self.assertTrue(result)
        self.mock_conn.commit.assert_called_once()

    def test_contact_insertion_all_fields_empty(self):
        """Test contact insertion with all fields empty (should not insert anything)"""
        # Mocking the database connection and cursor to avoid actual DB interaction
        with patch('pages.crm_contact_app.get_db_connection') as mock_get_db_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_get_db_conn.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            # Hardcoding the 'country' value for consistency (as done in UI auto-fill)
            country_value = "Australia"

            # Call the insert_contact function with all fields empty, but hardcoded country
            result = insert_contact(
                "", "", "",  # All fields empty
                "", "", "",
                "", "", "", 
                country_value  # Hardcoded country as 'Australia'
            )

            # Assert that execute was not called (no insertion should happen)
            mock_cursor.execute.assert_not_called()

            # Ensure the function returned False
            self.assertFalse(result)


    def tearDown(self):
        """Clean up any necessary cleanup after tests."""
        if hasattr(self, 'mock_conn'):
            self.mock_conn.close()

if __name__ == '__main__':
    unittest.main()
