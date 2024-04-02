import os
from dotenv import load_dotenv

# Load environment variables from .env file
if load_dotenv():
    print("Environment variables loaded successfully.")
else:
    print("Failed to load environment variables from .env file.")

# Access environment variables
username = os.getenv('BETFAIR_USERNAME')
password = os.getenv('BETFAIR_PASSWORD')
app_key = os.getenv('BETFAIR_APP_KEY')

# Check if the environment variables are loaded and print a message accordingly
if username and password and app_key:
    print("Successfully retrieved environment variables:")
    print(f"BETFAIR_USERNAME: {username}")
    print(f"BETFAIR_PASSWORD: {password}")
    print(f"BETFAIR_APP_KEY: {app_key}")
else:
    print("Error: One or more environment variables are missing.")
