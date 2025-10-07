from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import logging
import streamlit as st
from google.auth.transport.requests import Request

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure Google OAuth
REDIRECT_URI = os.getenv("REDIRECT_URI")
CLIENT_SECRETS_FILE = "client_secrets.json"

if not os.path.exists(CLIENT_SECRETS_FILE):
    logging.error(f"Critical Error: The credentials file '{CLIENT_SECRETS_FILE}' was not found.")
    raise FileNotFoundError(f"Credentials file '{CLIENT_SECRETS_FILE}' not found.")

if not REDIRECT_URI:
    logging.error("Critical Error: REDIRECT_URI is not configured in your .env file.")
    raise ValueError("REDIRECT_URI is not configured in your .env file.")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
if "flow" not in st.session_state:
    st.session_state["flow"] = Flow.from_client_secrets_file(
        client_secrets_file=CLIENT_SECRETS_FILE,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
        redirect_uri=REDIRECT_URI,
    )

flow = st.session_state["flow"]

if "credentials" in st.session_state:
    flow.credentials = st.session_state["credentials"]

# if hasattr(flow, "credentials") and flow.credentials:
#     if flow.credentials.expired:
#         try:
#             flow.credentials.refresh(Request())
#             logging.info("Access token refreshed.")
#         except ValueError as e:
#             logging.error(f"Failed to refresh access token: {e}")
#             raise ValueError("No valid credentials found. Did you call fetch_token?")
# else:
#     logging.error("No credentials found. Did you call fetch_token?")
#     raise ValueError("No credentials found. Did you call fetch_token?")

def get_google_auth_url():
    authorization_url, state = flow.authorization_url(    
        access_type='offline',
        include_granted_scopes='true'
    )
    logging.info(f"Generated state: {state}")  # Log the generated state
    st.session_state["state"] = state
    return authorization_url

def process_google_login(query_params):
    try:
        logging.info(f"Query parameters received: {query_params}")
        
        # Validate the state parameter
        if "state" not in query_params or query_params["state"] != st.session_state.get("state"):
            raise ValueError("Login failed: State mismatch.")
        
        # Ensure the authorization code is present
        if "code" not in query_params:
            raise ValueError("Login failed: Missing authorization code.")
        
        # Construct the full authorization response URL
        base_url = REDIRECT_URI
        query_string = "&".join([f"{key}={value}" for key, value in query_params.items()])
        full_url = f"{base_url}?{query_string}"
        
        logging.info(f"Authorization response URL: {full_url}")
        
        # Use flow.fetch_token to exchange the authorization code for tokens
        response = flow.fetch_token(authorization_response=full_url, state=st.session_state.get("state"))
        st.session_state["credentials"] = flow.credentials
        logging.info(f"Token response: {response}")
        
        # Extract credentials and verify the ID token
        credentials = flow.credentials
        client_id = flow.client_config['client_id']
        request = google_requests.Request()
        id_info = id_token.verify_oauth2_token(
            id_token=credentials.id_token,
            request=request,
            audience=client_id
        )
        
        # Extract user information
        email = id_info.get("email")
        name = id_info.get("name")
        google_id = id_info.get("sub")
        
        # Extract refresh token
        refresh_token = credentials.refresh_token
        logging.info(f"Refresh Token: {refresh_token}")
        
        return email, name, google_id, refresh_token
    except Exception as e:
        logging.error(f"An error occurred during login: {e}")
        raise e

def refresh_access_token():
    try:
        if flow.credentials.expired:
            flow.credentials.refresh(Request())
            logging.info("Access token refreshed.")
            return flow.credentials.token
        else:
            logging.info("Access token is still valid.")
            return flow.credentials.token
    except Exception as e:
        logging.error(f"An error occurred while refreshing the access token: {e}")
        raise e