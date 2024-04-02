import os
import logging
from flask import Flask, send_file
from flumine import Flumine, clients
from bkstrat import FlatKashModel, FlatIggyModel
from betfairlightweight import APIClient
from betfairlightweight.filters import streaming_market_filter
from dotenv import load_dotenv
from flask_cors import CORS
from betfair_client import get_betfair_client
from flumine.clients import BetfairClient, ExchangeType

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='server.log', filemode='w')
logger = logging.getLogger(__name__)

username = os.getenv("BETFAIR_USERNAME")
password = os.getenv("BETFAIR_PASSWORD")  # Not needed for non-interactive login, can be removed if only using certs
app_key = os.getenv("BETFAIR_APP_KEY")
certs = os.getenv('BETFAIR_CERT_PATH')  # Ensure this points to your certificates directory

app = Flask(__name__)
CORS(app)

# Initialize the Betfair API client
betfair_client = get_betfair_client()

# Initialize the Flumine framework with the Betfair client
flumine_client = BetfairClient(get_betfair_client())

framework = Flumine(client=flumine_client)

# Define the strategies
thoroughbreds_strategy = FlatKashModel(
    market_filter=streaming_market_filter(
        event_type_ids=["7"],  # Horse Racing
        country_codes=["AU"],  # Australian Markets
        market_types=["WIN"],  # Win Markets
    ),
    max_order_exposure=50,
    max_trade_count=1,
    max_live_trade_count=1,
)

greyhounds_strategy = FlatIggyModel(
    market_filter=streaming_market_filter(
        event_type_ids=["4339"],  # Greyhound Racing
        country_codes=["AU"],  # Australian Markets
        market_types=["WIN"],  # Win Markets
    ),
    max_order_exposure=50,
    max_trade_count=1,
    max_live_trade_count=1,
)

def start_bot():
    logger.info("Starting the betting bot.")
    framework = Flumine(client=clients.BetfairClient(get_betfair_client()))
    framework.add_strategy(thoroughbreds_strategy)
    framework.add_strategy(greyhounds_strategy)
    framework.run()

def stop_bot():
    logger.info("Stopping the betting bot.")
    framework.stop()
    framework.remove_strategy(thoroughbreds_strategy)
    framework.remove_strategy(greyhounds_strategy)

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        return send_file('server.log', mimetype='text/plain', as_attachment=True)
    except FileNotFoundError:
        return "Log file not found", 404

@app.route("/start", methods=["POST"])

def start_bot_endpoint():
    try:
        start_bot()
        return "Bot started successfully", 200
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return f"Error starting bot: {str(e)}", 500

@app.route("/stop", methods=["POST"])
def stop_bot_endpoint():
    try:
        stop_bot()
        return "Bot stopped successfully", 200
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return f"Error stopping bot: {str(e)}", 500

if __name__ == "__main__":
    logger.info("Starting the server...")
    app.run(host='0.0.0.0', port=5000)
    logger.info("Server stopped.")
