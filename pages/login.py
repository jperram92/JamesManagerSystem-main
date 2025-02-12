import streamlit as st
import sqlite3
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

# Database functions
def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn

def check_password_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'password' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
        conn.commit()
    conn.close()

def create_user_table():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    check_password_column()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password, name):
    conn = get_db_connection()
    hashed_password = hash_password(password)
    try:
        conn.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
                     (email, hashed_password, name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_db_connection()
    hashed_password = hash_password(password)
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                        (email, hashed_password)).fetchone()
    conn.close()
    return dict(user) if user else None

def login_form():
    with st.form("login_form"):
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            user = authenticate_user(email, password)
            if user:
                st.session_state.user = user
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

def register_form():
    with st.form("register_form"):
        st.subheader("Register")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")

        if submit:
            if create_user(email, password, name):
                st.success("Registration successful! Please log in.")
            else:
                st.error("Registration failed. Email may already be in use.")

def logout():
    st.session_state.clear()
    st.experimental_rerun()

# Main app logic
def main():
    create_user_table()
    st.title("Custom Login System")

    if 'user' not in st.session_state:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            login_form()
        
        with tab2:
            register_form()
    else:
        st.write(f"Welcome, {st.session_state.user['name']}!")
        if st.button("Logout"):
            logout()

if __name__ == "__main__":
    main()
