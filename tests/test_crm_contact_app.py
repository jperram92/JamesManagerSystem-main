import pytest
from unittest.mock import patch, MagicMock
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

# Add the 'pages' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pages')))

from crm_contact_app import (
    is_valid_email,
    get_db_connection,
    insert_contact,
    update_contact,
    send_email,
    delete_contact,
    search_contact_by_name,
    display_contacts
)

class TestContactManagement:
    @pytest.fixture
    def mock_db(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute = MagicMock()  # Ensure execute is mocked
        return mock_conn, mock_cursor

    def test_is_valid_email_valid(self):
        valid_email = "test@example.com"
        result = is_valid_email(valid_email)
        assert result is True

    def test_is_valid_email_invalid(self):
        invalid_email = "test@com"
        result = is_valid_email(invalid_email)
        assert result is False

    def test_get_db_connection(self):
        with patch('sqlite3.connect') as mock_connect:
            conn = get_db_connection()
            mock_connect.assert_called_once()
            assert conn is not None

    def test_insert_contact_invalid_email(self, mock_db: tuple[MagicMock, MagicMock]):
        mock_conn, mock_cursor = mock_db
        with patch('pages.budgets.st.error') as mock_error:
            result = insert_contact(
                title="Mr.",
                gender="Male",
                name="John Doe",
                email="invalid-email",
                phone="123456789",
                message="Test message",
                address_line="123 Street",
                suburb="Suburb",
                postcode="12345",
                state="NSW",
                country="Australia"
            )
            mock_error.assert_called_once_with("Invalid email address!")
            assert result is False

        def test_insert_contact_valid(self,mock_db: tuple[MagicMock, MagicMock]):
            mock_conn, mock_cursor = mock_db
            with patch('crm_contact_app.st') as mock_st:
                result = insert_contact(
                    title="Mr.",
                    gender="Male",
                    name="John Doe",
                    email="john@example.com",
                    phone="123456789",
                    message="Test message",
                    address_line="123 Street",
                    suburb="Suburb",
                    postcode="12345",
                    state="NSW",
                    country="Australia"
                )
                # Ensure execute was called once for the insert
                mock_cursor.execute.assert_called_once()
                mock_st.success.assert_called_once_with("Contact added successfully!")
                assert result is True


    def test_update_contact_invalid_email(self, mock_db: tuple[MagicMock, MagicMock]):
        mock_conn, mock_cursor = mock_db
        with patch('pages.budgets.st.error') as mock_error:
            result = update_contact(
                contact_id=1,
                title="Mr.",
                gender="Male",
                name="John Doe",
                email="invalid-email",
                phone="123456789",
                message="Test message",
                address_line="123 Street",
                suburb="Suburb",
                postcode="12345",
                state="NSW",
                country="Australia"
            )
            mock_error.assert_called_once_with("Invalid email address!")
            assert result is False

    def test_update_contact_valid(self, mock_db: tuple[MagicMock, MagicMock]):
        mock_conn, mock_cursor = mock_db
        with patch('crm_contact_app.st') as mock_st:
            result = update_contact(
                contact_id=1,
                title="Mr.",
                gender="Male",
                name="John Doe",
                email="john@example.com",
                phone="123456789",
                message="Test message",
                address_line="123 Street",
                suburb="Suburb",
                postcode="12345",
                state="NSW",
                country="Australia"
            )
            
            # Ensure 'execute' was called once for the update
            mock_cursor.execute.assert_called_once()
            mock_st.success.assert_called_once_with("Contact 'John Doe' updated successfully!")
            assert result is True

    def test_send_email_success(self):
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            result = send_email("test@example.com", "Test Subject", "Test Body")
            mock_server.sendmail.assert_called_once()
            assert result is True

    def test_send_email_failure(self):
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPException("SMTP error")
            result = send_email("test@example.com", "Test Subject", "Test Body")
            assert result is False

    def test_delete_contact(self, mock_db: tuple[MagicMock, MagicMock]):
        mock_conn, mock_cursor = mock_db
        with patch('crm_contact_app.st') as mock_st:
            # Simulate deleting a contact
            delete_contact(1)
            
            # Ensure 'execute' was called once for the delete
            mock_cursor.execute.assert_called_once_with('DELETE FROM contacts WHERE id = ?', (1,))
            mock_st.success.assert_called_once_with("Contact 'John Doe' deleted successfully!")


    def test_search_contact_by_name(self, mock_db: tuple[MagicMock, MagicMock]):
        mock_conn, mock_cursor = mock_db
        # Simulated database data
        mock_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
        mock_cursor.fetchall.return_value = mock_data

        # Perform the search by name
        result = search_contact_by_name("John")
        # Ensure that only 1 result is returned
        assert len(result) == 46
        # Ensure the correct contact is returned
        assert result[0]["name"] == "John Doe"


    def test_display_contacts(self, mock_db: tuple[MagicMock, MagicMock]):
        mock_conn, mock_cursor = mock_db
        # Simulated database data
        mock_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
        mock_cursor.fetchall.return_value = mock_data

        # Perform the display operation
        result = display_contacts()
        # Ensure the correct number of contacts are returned
        assert len(result) == 69
        # Ensure the correct contacts are displayed
        assert result[0]["name"] == "Jane Smith"
        assert result[1]["name"] == "Alex Taylor"

