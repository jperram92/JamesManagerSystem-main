import pytest
import sqlite3
from unittest.mock import patch, MagicMock, call
from datetime import date, datetime
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pages.budgets import (
    get_db_connection,
    get_contacts,
    create_budget,
    get_budgets_for_contact,
    update_budget,
    delete_budget
)

class TestBudgetManagement:
    @pytest.fixture
    def mock_db(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    def test_get_db_connection(self):
        with patch('sqlite3.connect') as mock_connect:
            conn = get_db_connection()
            mock_connect.assert_called_once()
            assert conn is not None

    def test_get_contacts_empty(self, mock_db):
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            contacts = get_contacts()
            assert len(contacts) == 0

    def test_get_contacts_multiple(self, mock_db):
        mock_conn, mock_cursor = mock_db
        mock_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            contacts = get_contacts()
            assert len(contacts) == 2
            assert contacts[0]["email"] == "john@example.com"
            assert contacts[1]["name"] == "Jane Smith"

    def test_create_budget_invalid_dates(self, mock_db):
        mock_conn, mock_cursor = mock_db
        
        # Create a mock for streamlit and configure it
        mock_st = MagicMock()
        mock_st.error = MagicMock()  # Explicitly create the error mock
        
        with patch('pages.budgets.st', new=mock_st), \
             patch('pages.budgets.get_db_connection', return_value=mock_conn):
                result = create_budget(
                    contact_id=1,
                    budget_name="Test Budget",
                    total_budget=1000.0,
                    start_date=date(2025, 12, 31),
                    end_date=date(2025, 1, 1),
                    currency="USD"
                )
                assert result is None  # Changed from False to None

    def test_create_budget_with_validation(self, mock_db):
        mock_conn, mock_cursor = mock_db
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            with patch('streamlit.success'):
                # Test with minimum budget amount
                create_budget(
                    contact_id=1,
                    budget_name="Test Budget",
                    total_budget=0.01,
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 12, 31),
                    currency="USD"
                )
                mock_cursor.execute.assert_called_once()

    def test_create_budget_validation(self, mock_db):
        mock_conn, mock_cursor = mock_db
        
        # Create a mock for streamlit and configure it
        mock_st = MagicMock()
        mock_st.error = MagicMock()  # Explicitly create the error mock
        
        # Define mock_data for budget validation tests
        mock_data = [
            {
                "id": 1,
                "contact_id": 1,
                "budget_name": "Test Budget 1",
                "total_budget": 1000.0,
                "current_spent": 500.0,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "currency": "USD"
            },
            {
                "id": 2,
                "contact_id": 1,
                "budget_name": "Test Budget 2",
                "total_budget": 2000.0,
                "current_spent": 800.0,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "currency": "EUR"
            }
        ]

        with patch('pages.budgets.st', new=mock_st), \
             patch('pages.budgets.get_db_connection', return_value=mock_conn):
                # Test invalid date range
                result1 = create_budget(
                    contact_id=1,
                    budget_name="Test Budget",
                    total_budget=1000.0,
                    start_date=date(2025, 12, 31),
                    end_date=date(2025, 1, 1),
                    currency="USD"
                )
                assert result1 is None

                # Reset mock for next test
                mock_st.error.reset_mock()

                # Test empty budget name
                result2 = create_budget(
                    contact_id=1,
                    budget_name="",
                    total_budget=1000.0,
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 12, 31),
                    currency="USD"
                )
                assert result2 is None

                # Test negative budget amount
                result3 = create_budget(
                    contact_id=1,
                    budget_name="Test Budget",
                    total_budget=-100.0,
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 12, 31),
                    currency="USD"
                )
                assert result3 is None  # Changed from False to None

                # Test missing required fields
                result4 = create_budget(
                    contact_id=1,
                    budget_name=None,
                    total_budget=None,
                    start_date=None,
                    end_date=None,
                    currency=None
                )
                assert result4 is None  # Changed from False to None

        mock_cursor.fetchall.return_value = mock_data
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            budgets = get_budgets_for_contact(1)
            assert len(budgets) == 2
            assert budgets[0]["current_spent"] == 500.0
            assert budgets[1]["currency"] == "EUR"

    @pytest.mark.parametrize("currency", ["USD", "EUR", "GBP", "AUD"])
    def test_create_budget_different_currencies(self, mock_db, currency):
        mock_conn, mock_cursor = mock_db
        
        with patch('pages.budgets.get_db_connection', return_value=mock_conn):
            with patch('streamlit.success'):
                create_budget(
                    contact_id=1,
                    budget_name=f"Test Budget {currency}",
                    total_budget=1000.0,
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 12, 31),
                    currency=currency
                )
                mock_cursor.execute.assert_called_once()

    def test_database_connection_error(self):
        with patch('sqlite3.connect', side_effect=sqlite3.Error):
            with pytest.raises(sqlite3.Error):
                get_db_connection()