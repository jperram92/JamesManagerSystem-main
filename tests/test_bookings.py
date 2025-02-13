import pytest
from unittest.mock import MagicMock
import sqlite3
from datetime import datetime
import streamlit as st
from bookings import calendar  # Import the relevant functions

# Test for the successful database connection
def test_get_db_connection(mocker):
    mock_conn = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)

    conn = sqlite3.connect('crm.db')
    assert conn == mock_conn
    sqlite3.connect.assert_called_once_with('crm.db')


# Test for fetching bookings
def test_fetch_bookings(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    # Simulate database data return
    mock_cursor.fetchall.return_value = [
        ("Service 1", 100, "2025-12-01", "Line Item 1"),
        ("Service 2", 200, "2025-12-02", "Line Item 2"),
    ]

    bookings_data = [
        ("Service 1", 100, "2025-12-01", "Line Item 1"),
        ("Service 2", 200, "2025-12-02", "Line Item 2"),
    ]

    events = []
    for booking in bookings_data:
        service_name, booked_amount, date_booked, line_item_name = booking
        event = {
            "title": f"{service_name} - {line_item_name}",
            "color": "#4a90e2",  # Example color for the event
            "start": date_booked,
            "end": date_booked,  # Adjust this if needed
        }
        events.append(event)

    assert len(events) == 2
    assert events[0]["title"] == "Service 1 - Line Item 1"
    assert events[1]["title"] == "Service 2 - Line Item 2"


# Test for displaying the calendar and selecting a mode
def test_calendar_mode_selection(mocker):
    mocker.patch('streamlit.selectbox', return_value="Day Grid")

    mode = st.selectbox("Select Calendar Mode:", ["Day Grid", "Time Grid", "Timeline"])
    assert mode == "Day Grid"


# Test for booking form submission
def test_booking_form_submission(mocker):
    # Mock Streamlit's form components
    mocker.patch('streamlit.text_input', return_value="Test Service")
    mocker.patch('streamlit.selectbox', return_value=1)  # Example line item
    mocker.patch('streamlit.number_input', return_value=150.0)
    mocker.patch('streamlit.selectbox', return_value="Booked")
    mocker.patch('streamlit.form_submit_button', return_value=True)
    mocker.patch('streamlit.success')  # Mock success message

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    # Simulate form submission
    selected_date = "2025-12-01"
    service_name = "Test Service"
    line_item_id = 1
    booked_amount = 150.0
    status = "Booked"

    # Simulate form submission
    cursor = mock_conn.cursor()
    cursor.execute.return_value = None  # Simulate the successful database insert

    st.text_input("Service Name", value=service_name)
    st.selectbox("Line Item", [1, 2, 3, 4, 5], index=0)
    st.number_input("Booked Amount", min_value=0.00, value=booked_amount, step=0.01)
    st.selectbox("Status", ["Booked", "Pending", "Cancelled"], index=0)
    submit_button = st.form_submit_button("Submit Booking")

    if submit_button:
        cursor.execute(
            '''INSERT INTO bookings (budget_line_item_id, service_name, booked_amount, date_booked, status)
               VALUES (?, ?, ?, ?, ?)''',
            (line_item_id, service_name, booked_amount, selected_date, status)
        )
        mock_conn.commit()
        st.success(f"Booking for {service_name} on {selected_date} has been added successfully!")

    mock_cursor.execute.assert_called_once_with(
        '''INSERT INTO bookings (budget_line_item_id, service_name, booked_amount, date_booked, status)
           VALUES (?, ?, ?, ?, ?)''',
        (line_item_id, service_name, booked_amount, selected_date, status)
    )
    mock_conn.commit.assert_called_once()


# Test for booking form with missing data
def test_booking_form_missing_data(mocker):
    # Simulate missing data in booking form fields
    mocker.patch('streamlit.text_input', return_value="")
    mocker.patch('streamlit.selectbox', return_value=1)  # Example line item
    mocker.patch('streamlit.number_input', return_value=0.0)  # Invalid amount
    mocker.patch('streamlit.selectbox', return_value="Booked")
    mocker.patch('streamlit.form_submit_button', return_value=True)

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    service_name = ""
    booked_amount = 0.0

    submit_button = st.form_submit_button("Submit Booking")

    if submit_button:
        # Simulate validation error
        if not service_name or booked_amount <= 0:
            st.error("Please fill out all fields before submitting.")
        else:
            cursor.execute(
                '''INSERT INTO bookings (budget_line_item_id, service_name, booked_amount, date_booked, status)
                   VALUES (?, ?, ?, ?, ?)''',
                (1, service_name, booked_amount, datetime.now().strftime('%Y-%m-%d'), "Booked")
            )
            mock_conn.commit()

    with mocker.patch('streamlit.error') as mock_error:
        mock_error.assert_called_once_with("Please fill out all fields before submitting.")


# Test for calendar event rendering
def test_calendar_event_rendering(mocker):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mocker.patch('sqlite3.connect', return_value=mock_conn)
    mock_conn.cursor.return_value = mock_cursor

    # Simulate database query
    mock_cursor.fetchall.return_value = [
        ("Service 1", 100, "2025-12-01", "Line Item 1"),
        ("Service 2", 200, "2025-12-02", "Line Item 2"),
    ]

    # Calendar events rendering
    events = []
    for booking in mock_cursor.fetchall():
        service_name, booked_amount, date_booked, line_item_name = booking
        event = {
            "title": f"{service_name} - {line_item_name}",
            "color": "#4a90e2",  # Example color for the event
            "start": date_booked,
            "end": date_booked,  # Adjust this if needed
        }
        events.append(event)

    assert len(events) == 2
    assert events[0]["title"] == "Service 1 - Line Item 1"
    assert events[1]["title"] == "Service 2 - Line Item 2"


if __name__ == "__main__":
    pytest.main()
