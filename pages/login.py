import streamlit as st
from auth0.authentication import GetToken
from auth0.management import Auth0

# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# Set up Auth0 configuration
auth0_domain = os.getenv("AUTH0_DOMAIN")
auth0_client_id = os.getenv("AUTH0_CLIENT_ID")
auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET")
auth0_audience = f"https://{auth0_domain}/api/v2/"

def login():
    st.markdown(
        f"""
        <a href="https://{auth0_domain}/authorize?response_type=code&client_id={auth0_client_id}&redirect_uri=http://localhost:8501/login&scope=openid%20profile%20email" target="_self">
            Login with Auth0
        </a>
        """,
        unsafe_allow_html=True
    )

def logout():
    st.session_state.clear()
    st.experimental_rerun()

# Main app logic
def main():
    st.title("Auth0 Login Example")

    if 'user' not in st.session_state:
        login()
    else:
        st.write(f"Welcome, {st.session_state.user['name']}!")
        if st.button("Logout"):
            logout()

    # Handle the callback
    if 'code' in st.query_params:
        code = st.query_params['code']
        get_token = GetToken(auth0_domain, auth0_client_id, auth0_client_secret)
        token = get_token.authorization_code(code, 'http://localhost:8501/login')
        
        # Use the access token to get user info
        auth0_management = Auth0(auth0_domain, token['access_token'])
        user_info = auth0_management.users.get(token['id_token'])
        
        st.session_state.user = user_info
        st.experimental_rerun()

if __name__ == "__main__":
    main()