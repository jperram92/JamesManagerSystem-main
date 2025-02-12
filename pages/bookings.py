import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to connect to the database
def get_db_connection():
    db_path = os.getenv('DATABASE_PATH', 'crm.db')
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign keys
    return conn

# Function to get all contacts
def get_contacts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT * FROM contacts
    ''')
    contacts = cursor.fetchall()
    conn.close()
    return contacts

# Function to get valid budgets for a contact
def get_valid_budgets_for_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT id, contact_id, budget_name, total_budget, current_spent, 
               (total_budget - current_spent) AS remaining_budget, start_date, end_date, currency, status
        FROM budgets 
        WHERE contact_id = ? AND status = 'active' AND end_date >= ?
    ''', (contact_id, datetime.now().date()))
    budgets = cursor.fetchall()
    conn.close()
    return budgets

# Function to get budget line items for a budget
def get_budget_line_items(budget_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT id, budget_id, line_item_name, allocated_amount, 
               (allocated_amount - spent_amount) AS remaining_amount, status
        FROM budget_line_items WHERE budget_id = ?
    ''', (budget_id,))
    line_items = cursor.fetchall()
    conn.close()
    return line_items

# Function to create a new booking
def create_booking(contact_id, line_item_id, booking_date, service_details):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO bookings (contact_id, line_item_id, booking_date, service_details)
            VALUES (?, ?, ?, ?)
        ''', (contact_id, line_item_id, booking_date, service_details))
        conn.commit()
        conn.close()
        st.success("Booking created successfully!")
    except sqlite3.Error as e:
        st.error(f"Error creating booking: {e}")

def get_bookings_for_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT b.id, b.service_name, b.booked_amount, b.date_booked, b.status, 
               li.line_item_name, bu.budget_name
        FROM bookings b
        JOIN budget_line_items li ON b.budget_line_item_id = li.id
        JOIN budgets bu ON li.budget_id = bu.id
        WHERE b.contact_id = ?
    ''', (contact_id,))
    bookings = cursor.fetchall()
    conn.close()
    return bookings

# Streamlit UI for booking management
st.title("Booking Management")

# Select contact by name
contacts = get_contacts()
contact_names = [f"{contact['name']} ({contact['email']})" for contact in contacts]
contact_selection = st.selectbox("Select a Contact by Name", contact_names)

# Get selected contact_id from selected contact name
contact_id = None
for contact in contacts:
    if f"{contact['name']} ({contact['email']})" == contact_selection:
        contact_id = contact['id']
        break

# Display existing budgets for the selected contact
if contact_id:
    budgets = get_valid_budgets_for_contact(contact_id)
    if budgets:
        st.subheader(f"Active Budgets for Contact: {contact_selection}")

        # Create a dataframe to display budgets
        budgets_df = pd.DataFrame(budgets)

        # Debugging step: Check if "status" is available in columns
        # st.write("Debug: Available columns", budgets_df.columns)

        # Ensure correct column mapping
        column_mapping = {
            0: 'id',
            1: 'contact_id',
            2: 'budget_name',
            3: 'total_budget',
            4: 'current_spent',
            5: 'remaining_budget',
            6: 'start_date',
            7: 'end_date',
            8: 'currency',
            9: 'status'  # Ensure "status" is here
        }

        # Ensure correct column names in DataFrame
        budgets_df.rename(columns=column_mapping, inplace=True)

        # Display the dataframe
        display_columns = ['id', 'budget_name', 'total_budget', 'current_spent', 
                           'start_date', 'end_date', 'currency', 'status']
        budgets_df = budgets_df[display_columns]

        # Display the dataframe in the UI
        st.dataframe(budgets_df)

        # Handle budget selection
        selected_budget = st.selectbox("Select Budget", budgets_df['budget_name'].tolist())
        selected_budget_id = budgets_df.loc[budgets_df['budget_name'] == selected_budget, 'id'].values[0]

        # Get associated line items for the selected budget
        line_items = get_budget_line_items(selected_budget_id)

        if line_items:
            line_item_names = [line_item['line_item_name'] for line_item in line_items]
            selected_line_item = st.selectbox("Select Line Item", line_item_names)

            # Get selected line_item_id
            selected_line_item_id = None
            for line_item in line_items:
                if line_item['line_item_name'] == selected_line_item:
                    selected_line_item_id = line_item['id']
                    break

            # Select booking date
            booking_date = st.date_input("Select Booking Date", min_value=datetime.now())

            # Select service details
            service_details = st.text_area("Enter Service Details")

            # Create booking button
            if st.button("Create Booking"):
                create_booking(contact_id, selected_line_item_id, booking_date, service_details)
        else:
            st.write("No line items found for this budget.")
    else:
        st.write("No active budgets found for this contact.")
else:
    st.write("Please select a contact to view their budgets.")
