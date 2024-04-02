import os
from dotenv import load_dotenv
import betfairlightweight

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials from environment variables
username = os.getenv('BETFAIR_USERNAME')
password = os.getenv('BETFAIR_PASSWORD')  # Not needed for non-interactive login
app_key = os.getenv('BETFAIR_APP_KEY')
certs_dir = os.getenv('BETFAIR_CERT_PATH')  # Directory containing the certificate and key

# Initialize the Betfair API client for non-interactive login with certificates
trading = betfairlightweight.APIClient(
    username=username,
    password=password,  # Not needed for non-interactive login
    app_key=app_key,
    certs=certs_dir  # Pass the directory containing the certs
)

# Test the connection
try:
    trading.login()  # Non-interactive login
    account_details = trading.account.get_account_details()
    print("Account details:", account_details)
    print("Login successful. The connection to the Betfair API is established.")
except betfairlightweight.exceptions.BetfairError as e:
    print(f"Login failed: {e}")
