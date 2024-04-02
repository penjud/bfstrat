import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='main.log', filemode='a')
logger = logging.getLogger(__name__)

def start_bot():
    try:
        response = requests.post('http://localhost:8000/start')
        if response.status_code == 200:
            logger.info("Bot started successfully")
        else:
            logger.error(f"Failed to start bot: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error starting bot: {e}")

def stop_bot():
    try:
        response = requests.post('http://localhost:8000/stop')
        if response.status_code == 200:
            logger.info("Bot stopped successfully")
        else:
            logger.error(f"Failed to stop bot: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error stopping bot: {e}")

if __name__ == "__main__":
    start_bot()