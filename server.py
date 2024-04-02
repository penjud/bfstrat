import logging
from flask import Flask, send_file, request
from bkstrat import FlatKashModel, FlatIggyModel
from betfairlightweight.filters import streaming_market_filter
from flumine.worker import BackgroundWorker
from flumine.events.events import TerminationEvent
from dotenv import load_dotenv
from flask_cors import CORS
from betfair_client import create_new_connection
from flumine.clients import BetfairClient
import datetime
from betfair_client import create_new_connection
from flumine import Flumine
from flumine import Flumine
from flumine import flumine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='betting_bot.log', filemode='a')
logger = logging.getLogger(__name__)

# Initialize the Flumine framework with the Betfair client
flumine_client = None  # Define the flumine_client variable

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

# Add strategies to the Flumine framework
framework.add_strategy(thoroughbreds_strategy)
framework.add_strategy(greyhounds_strategy)

# Define the termination logic
def terminate(flumine) -> None:
    markets = list(flumine.markets.markets.values())
    markets_today = [m for m in markets if m.market_start_datetime.date() == datetime.datetime.utcnow().date()]
    if len(markets_today) == 0:
        flumine.handler_queue.put(TerminationEvent(flumine))

# Background worker for the termination logic
framework.add_worker(
    BackgroundWorker(
        framework,
        lambda: terminate(framework),
        interval=60,
        start_delay=60,
    )
)

app = Flask(__name__)
CORS(app)

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        return send_file('betting_bot.log', mimetype='text/plain', as_attachment=True)
    except FileNotFoundError:
        return "Log file not found", 404

@app.route("/start", methods=["POST"])
def start_bot_endpoint():
    try:
        logger.info("Starting the bot...")
        betfair_client = create_new_connection()
        flumine_client = BetfairClient(betfair_client)
        # Rest of the code...

        framework = Flumine(client=flumine_client)

        # Create a single MarketStream instance
        # Rest of the code...

        market_stream = flumine.streams.MarketStream(
                    flumine=framework,
                    unique_id=1000,
                    stream_type=flumine.streams.MarketStream,
                    market_filter=streaming_market_filter(
                        event_type_ids=["7", "4339"],
                        country_codes=["AU"],
                        market_types=["WIN"],
                    ),
                    market_data_filter=None,
                )

                # Add the MarketStream to the framework
        framework.add_stream(market_stream)
        
        framework.add_strategy(thoroughbreds_strategy)
        framework.add_strategy(greyhounds_strategy)
        
        try:
            framework.run()
        except Exception as e:
            logger.error(f"Error running the framework: {e}", exc_info=True)
            raise
        logger.info("Bot started successfully")
        return "Bot started successfully", 200
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        return f"Error starting bot: {str(e)}", 500

if __name__ == "__main__":
    logger.info("Starting the server...")
    app.run(host='0.0.0.0', port=5000)
    logger.info("Server stopped.")