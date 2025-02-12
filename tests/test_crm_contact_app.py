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

# Function to setup a fresh blank database before each test
def setup_test_db():
    if os.path.exists('crm.db'):
        os.remove('crm.db')

    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('DROP TABLE IF EXISTS budget_line_items')
    cursor.execute('DROP TABLE IF EXISTS budgets')
    cursor.execute('DROP TABLE IF EXISTS contacts')
    cursor.execute('DROP TABLE IF EXISTS applications')
    cursor.execute('DROP TABLE IF EXISTS application_documents')
    cursor.execute('DROP TABLE IF EXISTS expenses')

    # Create contacts table
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        gender TEXT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        message TEXT NOT NULL,
        address_line TEXT,
        suburb TEXT,
        postcode TEXT,
        state TEXT,
        country TEXT
    )
    ''')

    # Create applications table
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        interest TEXT NOT NULL,
        reason TEXT NOT NULL,
        skillsets TEXT NOT NULL,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    )
    ''')

    # Create application_documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS application_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        document_name TEXT,
        document_path TEXT,
        signature BLOB,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    )
    ''')

    # Create budgets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        budget_name TEXT NOT NULL,
        total_budget DECIMAL(10, 2),
        current_spent DECIMAL(10, 2) DEFAULT 0.00,
        remaining_budget AS (total_budget - current_spent),
        start_date DATE,
        end_date DATE,
        currency TEXT,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    )
    ''')

    # Create budget_line_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budget_line_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        budget_id INTEGER,
        line_item_name TEXT NOT NULL,
        allocated_amount DECIMAL(10, 2),
        spent_amount DECIMAL(10, 2) DEFAULT 0.00,
        remaining_amount AS (allocated_amount - spent_amount),
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (budget_id) REFERENCES budgets(id)
    )
    ''')

    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        line_item_id INTEGER,
        product_name TEXT NOT NULL,
        product_group TEXT,
        rate DECIMAL(10, 2),
        frequency TEXT CHECK(frequency IN ('hourly', 'daily', 'weekly', 'monthly', 'yearly')),
        service_name TEXT,
        description TEXT,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (line_item_id) REFERENCES budget_line_items(id)
    )
    ''')

    # Create expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        line_item_id INTEGER,
        product_id INTEGER,
        amount DECIMAL(10, 2),
        quantity DECIMAL(10, 2),
        date_incurred DATE,
        description TEXT,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (line_item_id) REFERENCES budget_line_items(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')

    # Insert sample data into contacts table
    cursor.executemany(''' 
    INSERT INTO contacts (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        ('Mr.', 'Male', 'John Doe', 'john.doe@example.com', '1234567890', 'Interested in testing.', '123 Main St', 'Somewhere', '1234', 'NSW', 'Australia'),
        ('Ms.', 'Female', 'Jane Smith', 'jane.smith@example.com', '0987654321', 'Looking to apply.', '456 Elm St', 'Anywhere', '5678', 'VIC', 'Australia'),
        ('Dr.', 'Non-binary', 'Alex Taylor', 'alex.taylor@example.com', '1122334455', 'Testing with dummy data.', '789 Oak St', 'Nowhere', '9101', 'QLD', 'Australia'),
        ('Prof.', 'Male', 'William Brown', 'william.brown@example.com', '2233445566', 'Trying the system out.', '101 Pine St', 'Everywhere', '1122', 'SA', 'Australia'),
        ('Ms.', 'Female', 'Emily White', 'emily.white@example.com', '3344556677', 'Just exploring.', '202 Maple St', 'Anywhere', '3344', 'WA', 'Australia')
    ])

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database, tables, and test data created successfully!")

class TestContactManagement:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        # Setup the test DB with sample data before each test
        setup_test_db()

    @pytest.fixture
    def mock_db(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute = MagicMock()  # Ensure execute is mocked
        return mock_conn, mock_cursor

    def test_insert_contact_valid(self, mock_db: tuple[MagicMock, MagicMock]):
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
            mock_cursor.execute.assert_called_once_with(
                "UPDATE contacts SET title = ?, gender = ?, name = ?, email = ?, phone = ?, message = ?, address_line = ?, suburb = ?, postcode = ?, state = ?, country = ? WHERE id = ?",
                ("Mr.", "Male", "John Doe", "john@example.com", "123456789", "Test message", "123 Street", "Suburb", "12345", "NSW", "Australia", 1)
            )
            mock_st.success.assert_called_once_with("Contact 'John Doe' updated successfully!")
            assert result is True

    def test_delete_contact(self, mock_db: tuple[MagicMock, MagicMock]):
        mock_conn, mock_cursor = mock_db
        with patch('crm_contact_app.st') as mock_st:
            # Simulate deleting a contact
            delete_contact(1)
            # Ensure 'execute' was called once for the delete
            mock_cursor.execute.assert_called_once_with('DELETE FROM contacts WHERE id = ?', (1,))
            mock_st.success.assert_called_once_with("Contact 'John Doe' deleted successfully!")

    def test_display_contacts(self, mock_db: tuple[MagicMock, MagicMock]):
        mock_conn, mock_cursor = mock_db
        # Simulated database data
        mock_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            {"id": 3, "name": "Alex Taylor", "email": "alex.taylor@example.com"},
            {"id": 4, "name": "William Brown", "email": "william.brown@example.com"},
            {"id": 5, "name": "Emily White", "email": "emily.white@example.com"}
        ]
        mock_cursor.fetchall.return_value = mock_data

        # Perform the display operation
        result = display_contacts()
        # Ensure the correct number of contacts are returned
        assert len(result) == 5
        # Ensure the correct contacts are displayed
        assert result[0]["name"] == "John Doe"
        assert result[4]["name"] == "Emily White"
