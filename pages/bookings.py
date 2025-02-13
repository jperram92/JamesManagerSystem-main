import streamlit as st
from streamlit_calendar import calendar
import sqlite3
from datetime import datetime

# Set up the page configuration
st.set_page_config(page_title="Customized Calendar Demo", page_icon="📅")

# New font and color scheme
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f7fc;
        }
        .fc-event {
            border-radius: 8px;
            font-weight: bold;
        }
        .fc-toolbar-title {
            font-size: 2.5rem;
            color: #4a90e2;
        }
        .fc-event-title {
            color: #ffffff;
            font-size: 1rem;
        }
        .fc-event-past {
            opacity: 0.7;
        }
        .fc-daygrid-day-number {
            color: #e14e52;
        }
        .fc-event-time {
            font-style: italic;
        }
    </style>
""", unsafe_allow_html=True)

# Custom calendar mode selector
calendar_modes = [
    "Day Grid", "Time Grid", "Timeline", 
    "Resource Day Grid", "Resource Time Grid", "Resource Timeline", 
    "List View", "Multi Month View"
]

mode = st.selectbox("Select Calendar Mode:", calendar_modes)

# Connect to SQLite database and retrieve booking data
conn = sqlite3.connect('crm.db')
cursor = conn.cursor()

# Fetch all bookings
cursor.execute('''SELECT b.service_name, b.booked_amount, b.date_booked, l.line_item_name 
                  FROM bookings b
                  JOIN budget_line_items l ON b.budget_line_item_id = l.id
                  WHERE b.status = 'Booked' AND b.date_booked >= ? 
                  ORDER BY b.date_booked''', (datetime.now().strftime('%Y-%m-%d'),))

bookings_data = cursor.fetchall()

# Close the connection
conn.close()

# Map the fetched data into a format suitable for the calendar
events = []
for booking in bookings_data:
    service_name, booked_amount, date_booked, line_item_name = booking
    event = {
        "title": f"{service_name} - {line_item_name}",
        "color": "#4a90e2",  # Example color for the event
        "start": date_booked,
        "end": date_booked,  # You can adjust this based on the actual duration if needed
    }
    events.append(event)

calendar_resources = [
    {"id": "room1", "building": "Main Office", "title": "Conference Room 1"},
    {"id": "room2", "building": "Main Office", "title": "Conference Room 2"},
    {"id": "room3", "building": "Annex", "title": "Meeting Room A"},
    {"id": "room4", "building": "Main Office", "title": "Cafeteria"},
    {"id": "room5", "building": "Annex", "title": "Training Room"},
]

calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "resources": calendar_resources,
    "selectable": "true",
}

# Display the calendar with customized styles
state = calendar(
    events=events,
    options=calendar_options,
    custom_css=""" 
    .fc-event-past {
        opacity: 0.7;
    }
    .fc-event-title {
        font-size: 1rem;
    }
    .fc-toolbar-title {
        font-size: 2.5rem;
        color: #4a90e2;
    }
    """,
    key=mode,
)

# Handle booking form when user clicks on a date
if state.get("dateSelected"):
    selected_date = state["dateSelected"]
    st.write(f"Selected Date: {selected_date}")

    # Booking Form for new booking
    with st.form(key="booking_form"):
        service_name = st.text_input("Service Name")
        line_item_id = st.selectbox("Line Item", [1, 2, 3, 4, 5])  # Example: Line items from your data
        booked_amount = st.number_input("Booked Amount", min_value=0.00, step=0.01)
        status = st.selectbox("Status", ["Booked", "Pending", "Cancelled"])

        submit_button = st.form_submit_button("Submit Booking")

        if submit_button:
            # Insert the new booking into the database
            conn = sqlite3.connect('crm.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bookings (budget_line_item_id, service_name, booked_amount, date_booked, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (line_item_id, service_name, booked_amount, selected_date, status))
            conn.commit()
            conn.close()
            st.success(f"Booking for {service_name} on {selected_date} has been added successfully!")

# Store the new events if they are modified
if state.get("eventsSet") is not None:
    st.session_state["events"] = state["eventsSet"]

st.write(state)
