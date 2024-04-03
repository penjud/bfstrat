import logging
from flask import Flask, request
from bkstrat import FlatKashModel, FlatIggyModel
from betfairlightweight.filters import streaming_market_filter
from betfair_client import create_new_connection
from flumine import Flumine, clients
import datetime
from betfair_client import close_connection
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='server.log', filemode='a')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variable to track bot running state
is_bot_running = False

# Initialize bot components outside request handlers to avoid multiple initializations
betfair_client = create_new_connection()
flumine_client = clients.BetfairClient(betfair_client)
framework = Flumine(client=flumine_client)
thoroughbreds_strategy = FlatKashModel(
    market_filter=streaming_market_filter(
        event_type_ids=["7"],
        country_codes=["AU"],
        market_types=["WIN"],
    ),
    max_order_exposure=1,
    max_trade_count=1,
    max_live_trade_count=1,
)
greyhounds_strategy = FlatIggyModel(
    market_filter=streaming_market_filter(
        event_type_ids=["4339"],
        country_codes=["AU"],
        market_types=["WIN"],
    ),
    max_order_exposure=1,
    max_trade_count=1,
    max_live_trade_count=1,
)
framework.add_strategy(thoroughbreds_strategy)
framework.add_strategy(greyhounds_strategy)

@app.route("/start", methods=["POST"])
def start_bot_endpoint():
    global is_bot_running
    if not is_bot_running:
        try:
            logger.info("Starting the bot...")
            framework.run()
            is_bot_running = True
            logger.info("Bot started successfully")
            return {"status": "success", "message": "Bot started successfully"}, 200
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return {"status": "error", "message": f"Error starting bot: {e}"}, 500
    else:
        return {"status": "error", "message": "Bot is already running"}, 400

@app.route("/stop", methods=["POST"])
def stop_bot_endpoint():
    global is_bot_running
    if is_bot_running:
        try:
            framework.stop()
            close_connection()
            is_bot_running = False
            logger.info("Bot stopped successfully")
            return {"status": "success", "message": "Bot stopped successfully"}, 200
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return {"status": "error", "message": f"Error stopping bot: {e}"}, 500
    else:
        return {"status": "error", "message": "Bot is not running"}, 400
    
if __name__ == "__main__":
    logger.info("Starting the server...")
    app.run(host='0.0.0.0', port=5000)
    logger.info("Server stopped.")
