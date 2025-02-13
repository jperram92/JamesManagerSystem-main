import pytest
from unittest.mock import MagicMock
import sqlite3
import streamlit as st
import sys
import os

# Add the 'pages' directory (parent of the 'tests' directory) to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pages')))

from application_form import (
    get_db_connection, 
    fetch_contacts, 
    insert_application, 
    application_form
)

# Test for successful DB connection
def test_get_db_connection_success(mocker):
    mock_conn = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)

    conn = get_db_connection()
    assert conn == mock_conn
    sqlite3.connect.assert_called_once_with(r'C:\Users\james\OneDrive\Desktop\JamesManagerSystem-main\crm.db')


# Test for failed DB connection
def test_get_db_connection_failure(mocker):
    mocker.patch('sqlite3.connect', side_effect=sqlite3.Error("Database connection failed"))

    conn = get_db_connection()
    assert conn is None


# Test for fetching contacts
def test_fetch_contacts(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}]

    contacts = fetch_contacts()
    assert len(contacts) == 1
    assert contacts[0]['name'] == 'John Doe'


# Test for inserting application data
def test_insert_application(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    insert_application(1, 'Interest', 'Reason', 'Skillsets')
    mock_cursor.execute.assert_called_once_with(
        ''' 
        INSERT INTO applications (contact_id, interest, reason, skillsets)
        VALUES (?, ?, ?, ?)
        ''', (1, 'Interest', 'Reason', 'Skillsets')
    )
    mock_conn.commit.assert_called_once()


# Test for application form with no contacts
def test_application_form_no_contacts(mocker):
    mocker.patch('your_module.fetch_contacts', return_value=[])

    with mocker.patch('streamlit.write') as mock_write:
        application_form()
        mock_write.assert_called_once_with("No contacts available. Please add contacts to proceed.")


# Test for application form submission
def test_application_form_with_submission(mocker):
    mocker.patch('your_module.fetch_contacts', return_value=[{'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'phone': '12345'}])
    mocker.patch('streamlit.selectbox', return_value='John Doe (john@example.com)')
    mocker.patch('streamlit.text_area', side_effect=['Interest', 'Reason', 'Skillsets'])
    mocker.patch('streamlit.button', return_value=True)

    with mocker.patch('streamlit.success') as mock_success:
        application_form()
        mock_success.assert_called_once_with("Application submitted successfully!")


# Test for application form with missing fields
def test_application_form_missing_fields(mocker):
    mocker.patch('your_module.fetch_contacts', return_value=[{'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'phone': '12345'}])
    mocker.patch('streamlit.selectbox', return_value='John Doe (john@example.com)')
    mocker.patch('streamlit.text_area', side_effect=['Interest', '', 'Skillsets'])
    mocker.patch('streamlit.button', return_value=True)

    with mocker.patch('streamlit.error') as mock_error:
        application_form()
        mock_error.assert_called_once_with("Please fill out all fields before submitting.")


# Test for application form when no interest is filled
def test_application_form_no_interest(mocker):
    mocker.patch('your_module.fetch_contacts', return_value=[{'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'phone': '12345'}])
    mocker.patch('streamlit.selectbox', return_value='John Doe (john@example.com)')
    mocker.patch('streamlit.text_area', side_effect=['', 'Reason', 'Skillsets'])
    mocker.patch('streamlit.button', return_value=True)

    with mocker.patch('streamlit.error') as mock_error:
        application_form()
        mock_error.assert_called_once_with("Please fill out all fields before submitting.")


# Test for displaying the contact info in the form
def test_application_form_display(mocker):
    mocker.patch('your_module.fetch_contacts', return_value=[{'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'phone': '12345'}])
    mocker.patch('streamlit.selectbox', return_value='John Doe (john@example.com)')
    mocker.patch('streamlit.text_area', side_effect=['Interest', 'Reason', 'Skillsets'])

    with mocker.patch('streamlit.write') as mock_write:
        application_form()
        mock_write.assert_any_call(f"Selected Contact: John Doe")
        mock_write.assert_any_call(f"Email: john@example.com")
        mock_write.assert_any_call(f"Phone: 12345")


# Test for button click and success
def test_application_form_button(mocker):
    mocker.patch('streamlit.button', return_value=True)
    with mocker.patch('streamlit.write') as mock_write:
        application_form()
        mock_write.assert_called_with("Application submitted successfully!")


if __name__ == '__main__':
    pytest.main()
