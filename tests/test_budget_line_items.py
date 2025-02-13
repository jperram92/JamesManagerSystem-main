import pytest
from unittest.mock import MagicMock
from unittest.mock import patch
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
from budget_line_items import (  # Adjust the import to match the actual filename
    get_db_connection,
    create_budget_line_item,
    create_product,
    get_budget_line_items,
    get_line_item_products,
    update_budget_line_item,
    update_product,
    delete_budget_line_item,
    delete_product,
    validate_budget_allocation,
    get_budget_details,
    get_contact_budgets,
    display_budget_line_items,
    add_expense,
    get_line_item_expenses,
    calculate_line_item_totals,
    manage_budget_line_items,
)

# Mock database connection and cursor
@pytest.fixture
def mock_db(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    return mock_conn, mock_cursor


# Test for database connection
def test_get_db_connection(mocker):
    mock_conn = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    conn = get_db_connection()
    assert conn == mock_conn
    sqlite3.connect.assert_called_once_with(r'C:\Users\james\OneDrive\Desktop\JamesManagerSystem-main\crm.db')


# Test creating a budget line item
def test_create_budget_line_item(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.lastrowid = 1
    line_item_id = create_budget_line_item(1, "New Line Item", 1000.00)
    assert line_item_id == 1
    mock_cursor.execute.assert_called_once_with(
        '''INSERT INTO budget_line_items (budget_id, line_item_name, allocated_amount)
           VALUES (?, ?, ?)''', (1, "New Line Item", 1000.00)
    )


# Test creating a product
def test_create_product(mock_db):
    mock_conn, mock_cursor = mock_db
    create_product(1, "Product 1", "Group 1", 100.00, "monthly", "Service 1", "Product description")
    mock_cursor.execute.assert_called_once_with(
        '''INSERT INTO products (line_item_id, product_name, product_group, rate, frequency, service_name, description)
           VALUES (?, ?, ?, ?, ?, ?, ?)''', (1, "Product 1", "Group 1", 100.00, "monthly", "Service 1", "Product description")
    )


# Test getting budget line items
def test_get_budget_line_items(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"id": 1, "line_item_name": "Line Item 1", "allocated_amount": 1000.00, "spent_amount": 500.00, "status": "Active", "currency": "USD"}
    ]
    line_items = get_budget_line_items(1)
    assert len(line_items) == 1
    assert line_items[0]['line_item_name'] == "Line Item 1"
    assert line_items[0]['allocated_amount'] == 1000.00


# Test updating a budget line item
def test_update_budget_line_item(mock_db):
    mock_conn, mock_cursor = mock_db
    update_budget_line_item(1, "Updated Line Item", 1200.00)
    mock_cursor.execute.assert_called_once_with(
        '''UPDATE budget_line_items SET line_item_name = ?, allocated_amount = ? WHERE id = ?''',
        ("Updated Line Item", 1200.00, 1)
    )


# Test updating a product
def test_update_product(mock_db):
    mock_conn, mock_cursor = mock_db
    update_product(1, "Updated Product", "New Group", 120.00, "monthly", "New Service", "Updated Description")
    mock_cursor.execute.assert_called_once_with(
        '''UPDATE products SET product_name = ?, product_group = ?, rate = ?, frequency = ?, service_name = ?, description = ? WHERE id = ?''',
        ("Updated Product", "New Group", 120.00, "monthly", "New Service", "Updated Description", 1)
    )


# Test deleting a budget line item
def test_delete_budget_line_item(mock_db):
    mock_conn, mock_cursor = mock_db
    delete_budget_line_item(1)
    mock_cursor.execute.assert_any_call('DELETE FROM products WHERE line_item_id = ?', (1,))
    mock_cursor.execute.assert_any_call('DELETE FROM budget_line_items WHERE id = ?', (1,))


# Test deleting a product
def test_delete_product(mock_db):
    mock_conn, mock_cursor = mock_db
    delete_product(1)
    mock_cursor.execute.assert_called_once_with('DELETE FROM products WHERE id = ?', (1,))


# Test validating budget allocation
def test_validate_budget_allocation(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {"total_budget": 5000.00}
    mock_cursor.fetchone.return_value = {"total_allocated": 3000.00}
    is_valid = validate_budget_allocation(1, 1500.00)
    assert is_valid is True
    is_valid = validate_budget_allocation(1, 2500.00)
    assert is_valid is False


# Test getting budget details
def test_get_budget_details(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "budget_name": "Test Budget",
        "total_budget": 5000.00,
        "currency": "USD",
        "total_allocated": 3000.00,
        "total_spent": 1500.00,
        "remaining_budget": 2000.00
    }
    budget_details = get_budget_details(1)
    assert budget_details["budget_name"] == "Test Budget"
    assert budget_details["total_budget"] == 5000.00
    assert budget_details["remaining_budget"] == 2000.00


# Test getting contact budgets
def test_get_contact_budgets(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"id": 1, "budget_name": "Budget 1", "total_budget": 5000.00, "currency": "USD"}
    ]
    budgets = get_contact_budgets(1)
    assert len(budgets) == 1
    assert budgets[0]["budget_name"] == "Budget 1"


# Test displaying budget line items
def test_display_budget_line_items(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"id": 1, "line_item_name": "Line Item 1", "allocated_amount": 1000.00, "spent_amount": 500.00, "status": "Active", "currency": "USD"}
    ]
    with patch('streamlit.dataframe') as mock_df:
        display_budget_line_items(1, "Test Budget")
        mock_df.assert_called_once()


# Test adding an expense
def test_add_expense(mock_db):
    mock_conn, mock_cursor = mock_db
    add_expense(1, 1, 100.00, 2, datetime.now().strftime('%Y-%m-%d'), "Test expense")
    mock_cursor.execute.assert_any_call(
        '''INSERT INTO expenses (line_item_id, product_id, amount, quantity, date_incurred, description)
           VALUES (?, ?, ?, ?, ?, ?)''', (1, 1, 100.00, 2, datetime.now().strftime('%Y-%m-%d'), "Test expense")
    )


# Test getting line item expenses
def test_get_line_item_expenses(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"id": 1, "amount": 100.00, "quantity": 2, "total_amount": 200.00, "date_incurred": "2025-12-01", "description": "Test expense", "product_name": "Product 1", "service_name": "Service 1"}
    ]
    expenses = get_line_item_expenses(1)
    assert len(expenses) == 1
    assert expenses[0]["product_name"] == "Product 1"


# Test calculating line item totals
def test_calculate_line_item_totals(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {"allocated_amount": 1000.00, "total_spent": 500.00, "remaining": 500.00}
    totals = calculate_line_item_totals(1)
    assert totals['allocated_amount'] == 1000.00
    assert totals['remaining'] == 500.00


# Test managing budget line items
def test_manage_budget_line_items(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"id": 1, "line_item_name": "Line Item 1", "allocated_amount": 1000.00, "spent_amount": 500.00, "status": "Active", "currency": "USD"}
    ]
    with patch('streamlit.selectbox') as mock_selectbox:
        manage_budget_line_items()
        mock_selectbox.assert_called_once()

# Test for failed database connection in get_db_connection
def test_get_db_connection_failure(mocker):
    mocker.patch('sqlite3.connect', side_effect=sqlite3.Error("Database connection failed"))
    conn = get_db_connection()
    assert conn is None


# Test for creating a budget line item with invalid data
def test_create_budget_line_item_invalid_data(mock_db):
    mock_conn, mock_cursor = mock_db
    # Test creating a budget line item with invalid allocated amount
    with pytest.raises(Exception):
        create_budget_line_item(1, "Invalid Line Item", -1000.00)


# Test for invalid product creation (e.g., missing fields)
def test_create_product_invalid(mock_db):
    mock_conn, mock_cursor = mock_db
    # Test creating a product with invalid rate (negative value)
    with pytest.raises(Exception):
        create_product(1, "Invalid Product", "Invalid Group", -50.00, "monthly", "Invalid Service", "Invalid Description")


# Test for getting budget line items with no data
def test_get_budget_line_items_empty(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    line_items = get_budget_line_items(1)
    assert len(line_items) == 0


# Test for updating a product with invalid data
def test_update_product_invalid(mock_db):
    mock_conn, mock_cursor = mock_db
    with pytest.raises(Exception):
        update_product(1, "Invalid Product", "New Group", -120.00, "monthly", "New Service", "Updated Description")


# Test for deleting a non-existent budget line item
def test_delete_non_existent_budget_line_item(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.execute.return_value = None
    delete_budget_line_item(9999)  # Assuming 9999 does not exist in the database
    mock_cursor.execute.assert_called_with('DELETE FROM budget_line_items WHERE id = ?', (9999,))


# Test for deleting a non-existent product
def test_delete_non_existent_product(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.execute.return_value = None
    delete_product(9999)  # Assuming 9999 does not exist in the database
    mock_cursor.execute.assert_called_with('DELETE FROM products WHERE id = ?', (9999,))


# Test for validating budget allocation with an amount greater than the total budget
def test_validate_budget_allocation_over_budget(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {"total_budget": 5000.00}
    is_valid = validate_budget_allocation(1, 6000.00)
    assert is_valid is False


# Test for getting budget details when there is no data
def test_get_budget_details_no_data(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None
    budget_details = get_budget_details(9999)  # Assuming 9999 does not exist in the database
    assert budget_details is None


# Test for getting contact budgets when there is no data
def test_get_contact_budgets_no_data(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    budgets = get_contact_budgets(9999)  # Assuming 9999 does not exist in the database
    assert len(budgets) == 0


# Test for adding an expense with a negative amount
def test_add_expense_negative_amount(mock_db):
    mock_conn, mock_cursor = mock_db
    with pytest.raises(Exception):
        add_expense(1, 1, -100.00, 2, datetime.now().strftime('%Y-%m-%d'), "Test negative expense")


# Test for calculating line item totals with no expenses
def test_calculate_line_item_totals_no_expenses(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {"allocated_amount": 1000.00, "total_spent": 0.00, "remaining": 1000.00}
    totals = calculate_line_item_totals(1)
    assert totals['total_spent'] == 0.00


# Test for checking total allocated with line item exceeding budget
def test_calculate_line_item_totals_exceeding_budget(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {"allocated_amount": 1000.00, "total_spent": 1500.00, "remaining": -500.00}
    totals = calculate_line_item_totals(1)
    assert totals['remaining'] == -500.00


# Test for fetching line item expenses when no data is present
def test_get_line_item_expenses_empty(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    expenses = get_line_item_expenses(1)
    assert len(expenses) == 0


# Test for managing budget line items when no data is found
def test_manage_budget_line_items_no_data(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    with patch('streamlit.selectbox') as mock_selectbox:
        manage_budget_line_items()
        mock_selectbox.assert_called_once()


# Test for handling exception during the database query in create_product
def test_create_product_db_exception(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.execute.side_effect = sqlite3.Error("Database error")
    with pytest.raises(sqlite3.Error):
        create_product(1, "Test Product", "Group", 100.00, "monthly", "Test Service", "Test Description")

# Test for invalid expense date
def test_add_expense_invalid_date(mock_db):
    mock_conn, mock_cursor = mock_db
    with pytest.raises(ValueError):
        add_expense(1, 1, 100.00, 2, "invalid-date", "Invalid expense date")

# Test for selecting non-existing product in expense creation
def test_add_expense_non_existing_product(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    # Simulate no product in the database
    mock_cursor.fetchall.return_value = []
    with pytest.raises(ValueError):
        add_expense(1, 9999, 100.00, 2, datetime.now().strftime('%Y-%m-%d'), "Non-existing product expense")

if __name__ == '__main__':
    pytest.main()
