import betfairlightweight
from dotenv import load_dotenv
import os
import threading
import time
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Retrieve credentials and certificate path from environment variables
username = os.getenv("BETFAIR_USERNAME")
password = os.getenv("BETFAIR_PASSWORD")
app_key = os.getenv("BETFAIR_APP_KEY")
certs_dir = os.getenv('BETFAIR_CERT_PATH')

# This is the singleton instance that will be used throughout the application
_betfair_client_instance = None
_client_lock = threading.Lock()

def create_new_connection():
    global _betfair_client_instance
    with _client_lock:
        if _betfair_client_instance is None:
            try:
                logger.info(f"Creating Betfair client with username: {username}, app_key: {app_key}, certs_dir: {certs_dir}")
                _betfair_client_instance = betfairlightweight.APIClient(username, password, app_key, certs_dir)
                _betfair_client_instance.login()
                logger.info("Betfair client created and logged in.")
            except Exception as e:
                logger.error(f"Failed to create and log in Betfair client: {e}", exc_info=True)
                _betfair_client_instance = None
    return _betfair_client_instance

def keep_alive(client):
    while True:
        try:
            client.keep_alive()
            logger.info("Keep-alive request sent.")
        except betfairlightweight.exceptions.APIError as e:
            logger.error(f"Failed to keep the session alive: {e}")
        time.sleep(60)  # Wait for 60 seconds before the next keep-alive request