import pytest
from unittest.mock import patch, MagicMock
import sqlite3
from io import BytesIO
from PIL import Image
import streamlit as st
from document_generator import (
    get_db_connection,
    save_signature_to_db,
    draw_signature,
    fetch_signature_and_timestamp_from_db,
    fetch_signature_from_db,
    fetch_contact_with_application,
    create_document,
    generate_and_download_pdf,
    document_page
)

# Test for database connection
def test_get_db_connection(mocker):
    mock_conn = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    conn = get_db_connection()
    assert conn == mock_conn
    sqlite3.connect.assert_called_once_with(r'C:\Users\james\OneDrive\Desktop\JamesManagerSystem-main\crm.db')


# Test saving signature to the database
def test_save_signature_to_db(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    # Mock signature image
    signature_image = Image.new('RGB', (100, 50), color='black')

    save_signature_to_db(1, signature_image)
    mock_cursor.execute.assert_called_once_with(
        '''UPDATE application_documents
           SET signature = ?, timestamp = ?
           WHERE contact_id = ?''', (MagicMock(), MagicMock(), 1)
    )


# Test drawing signature and saving it to DB
def test_draw_signature(mocker):
    mocker.patch('streamlit.title')
    mocker.patch('streamlit.subheader')
    mocker.patch('streamlit.button', return_value=True)
    mocker.patch('streamlit.image')

    # Mock canvas result
    mock_canvas_result = MagicMock()
    mock_canvas_result.image_data = b'fake_image_data'
    mocker.patch('streamlit_drawable_canvas.st_canvas', return_value=mock_canvas_result)

    # Run the function
    draw_signature(1)

    # Check if signature image was passed to save_signature_to_db
    save_signature_to_db.assert_called_once_with(1, MagicMock())


# Test fetching signature and timestamp from DB
def test_fetch_signature_and_timestamp_from_db(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = [b'fake_signature_data', '2025-12-01 12:00:00']

    signature_image, timestamp = fetch_signature_and_timestamp_from_db(1)

    assert signature_image is not None
    assert timestamp == '2025-12-01 12:00:00'


# Test creating the document with signature
def test_create_document(mocker):
    # Mock signature image and other fields
    signature_image = MagicMock()
    contact_name = "John Doe"
    contact_email = "john@example.com"
    contact_phone = "1234567890"
    document_name = "Test Document"
    interest = "Developer"
    reason = "To contribute to project"
    skillsets = "Python, JavaScript"

    pdf_output = create_document(contact_name, contact_email, contact_phone, document_name, interest, reason, skillsets, signature_image)

    assert pdf_output is not None
    assert isinstance(pdf_output, BytesIO)


# Test generating and downloading the PDF
def test_generate_and_download_pdf(mocker):
    mocker.patch('streamlit.markdown')
    mocker.patch('your_module.fetch_signature_and_timestamp_from_db', return_value=(MagicMock(), '2025-12-01 12:00:00'))

    generate_and_download_pdf("John Doe", "john@example.com", "1234567890", "Test Document", "Developer", "To contribute to project", "Python, JavaScript", 1, MagicMock())

    st.markdown.assert_called_once_with(MagicMock(), unsafe_allow_html=True)


# Test document page with contacts
def test_document_page_with_contacts(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    # Mock contacts
    mock_cursor.fetchall.return_value = [(1, 'John Doe', 'john@example.com', '1234567890')]

    mocker.patch('streamlit.selectbox', return_value="John Doe")
    mocker.patch('streamlit.write')

    document_page()

    st.write.assert_called_once_with("Contact ID: 1")


# Test add expense function
def test_add_expense(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    add_expense(1, 1, 100.00, 2, "2025-12-01", "Test expense")

    mock_cursor.execute.assert_any_call(
        '''INSERT INTO expenses (line_item_id, product_id, amount, quantity, date_incurred, description)
           VALUES (?, ?, ?, ?, ?, ?)''', (1, 1, 100.00, 2, "2025-12-01", "Test expense")
    )


# Test calculating line item totals
def test_calculate_line_item_totals(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (1000.00, 500.00, 500.00)

    totals = calculate_line_item_totals(1)

    assert totals['allocated_amount'] == 1000.00
    assert totals['total_spent'] == 500.00
    assert totals['remaining'] == 500.00


# Test error case for database connection
def test_get_db_connection_error(mocker):
    mocker.patch('sqlite3.connect', side_effect=sqlite3.Error("Database connection error"))
    
    conn = get_db_connection()
    assert conn is None


# Test error case for save signature to DB
def test_save_signature_to_db_error(mocker):
    mocker.patch('sqlite3.connect', side_effect=sqlite3.Error("Database error"))
    
    signature_image = MagicMock()
    save_signature_to_db(1, signature_image)  # It should not raise an error


# Test signature drawing and saving
def test_draw_signature_no_signature(mocker):
    mocker.patch('streamlit.title')
    mocker.patch('streamlit.subheader')
    mocker.patch('streamlit.button', return_value=True)
    mocker.patch('streamlit.image')

    mock_canvas_result = MagicMock()
    mock_canvas_result.image_data = None
    mocker.patch('streamlit_drawable_canvas.st_canvas', return_value=mock_canvas_result)

    draw_signature(1)  # Should not crash even if no signature is drawn


# Test successful signature fetch
def test_fetch_signature_from_db(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = [b'fake_signature_data']
    
    signature_image = fetch_signature_from_db(1)
    assert signature_image is not None


# Test no signature available
def test_fetch_signature_no_signature(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = [None]
    
    signature_image = fetch_signature_from_db(1)
    assert signature_image is None


# Test contact and application fetch failure
def test_fetch_contact_with_application_no_data(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None
    
    contact_data = fetch_contact_with_application(1)
    assert contact_data is None


# Test fetching contacts for document page
def test_document_page_no_contacts(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []
    
    with patch('streamlit.write') as mock_write:
        document_page()
        mock_write.assert_called_once_with("No contacts found in the database.")


if __name__ == "__main__":
    pytest.main()
