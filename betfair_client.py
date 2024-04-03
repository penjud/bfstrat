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

# Counter for active connections
active_connections = 0

def create_new_connection():
    global _betfair_client_instance, active_connections
    with _client_lock:
        if _betfair_client_instance is None:
            try:
                logger.info(f"Creating Betfair client with username: {username}, app_key: {app_key}, certs_dir: {certs_dir}")
                _betfair_client_instance = betfairlightweight.APIClient(username, password, app_key, certs_dir)
                _betfair_client_instance.login()
                logger.info("Betfair client created and logged in.")
                # Increment the counter when a new connection is successfully created
                active_connections += 1
                logger.info(f"Active connections: {active_connections}")
            except Exception as e:
                logger.error(f"Failed to create and log in Betfair client: {e}", exc_info=True)
                _betfair_client_instance = None
    return _betfair_client_instance

def keep_alive(client):
    while True:
        try:
            response = client.keep_alive()
            logger.info(f"Keep-alive request sent. Response: {response}")
        except betfairlightweight.exceptions.APIError as e:
            if "IP restriction" in str(e) or "unusual traffic" in str(e):
                logger.error(f"IP restriction or unusual traffic detected: {e}")
            else:
                logger.error(f"Failed to keep the session alive: {e}")
        time.sleep(60) # Wait for 60 seconds before the next keep-alive request

# Ensure the connection is created before starting the thread
_betfair_client_instance = create_new_connection()

# Start the keep_alive thread only if the connection was successfully created
if _betfair_client_instance is not None:
    keep_alive_thread = threading.Thread(target=keep_alive, args=(_betfair_client_instance,))
    keep_alive_thread.start()
else:
    logger.error("Failed to create Betfair client connection. Exiting.")
    exit(1)

def close_connection():
    global _betfair_client_instance, active_connections
    if _betfair_client_instance is not None:
        try:
            _betfair_client_instance.logout()
            logger.info("Betfair client logged out.")
            # Decrement the counter when a connection is closed
            active_connections -= 1
            logger.info(f"Active connections: {active_connections}")
        except Exception as e:
            logger.error(f"Failed to log out Betfair client: {e}", exc_info=True)
        _betfair_client_instance = None
