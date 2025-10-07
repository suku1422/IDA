import logging
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Configuration settings
REDIRECT_URI = os.getenv("REDIRECT_URI")
CLIENT_SECRETS_FILE = "client_secrets.json"

# Check if the secrets file and redirect URI are available
if not os.path.exists(CLIENT_SECRETS_FILE):
    logging.error(f"Critical Error: The credentials file '{CLIENT_SECRETS_FILE}' was not found. Please download it from Google Cloud Console.")
    raise FileNotFoundError(f"Credentials file '{CLIENT_SECRETS_FILE}' not found.")
if not REDIRECT_URI:
    logging.error("Critical Error: REDIRECT_URI is not configured in your .env file.")
    raise ValueError("REDIRECT_URI is not configured in your .env file.")