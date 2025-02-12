import streamlit as st
import sqlite3
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# Database functions
def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn

# Hash password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

# Create user and store the hashed password
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

# Authenticate user by comparing the entered password with the stored hash
def authenticate_user(email, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user['password']):
        return dict(user)
    return None

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
                st.rerun()
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
    st.rerun()

# Main app logic
def main():
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
