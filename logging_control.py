import logging
from flumine.order.ordertype import OrderTypes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class OrderProcessor:
    def __init__(self):
        self.orders = []

    def _setup(self):
        self.orders = []

    def _process_cleared_orders_meta(self, event):
        orders = event.event
        for order in orders:
            try:
                if order.order_type.ORDER_TYPE == OrderTypes.LIMIT:
                    size = order.order_type.size
                    price = order.order_type.price
                else:
                    size = order.order_type.liability
                    price = None

                order_data = {
                    "bet_id": order.bet_id,
                    "strategy_name": order.trade.strategy,
                    "market_id": order.market_id,
                    "selection_id": order.selection_id,
                    "trade_id": order.trade.id,
                    "date_time_placed": order.responses.date_time_placed,
                    "price": price,
                    "size": size,
                    "size_matched": order.size_matched,
                    "profit": order.profit,
                    "side": order.side.value,
                    "elapsed_seconds_executable": order.elapsed_seconds_executable,
                    "order_status": order.status.value,
                    "market_note": order.trade.market_notes,
                    "trade_notes": order.trade.notes_str,
                    "order_notes": order.notes_str,
                }

                self.orders.append(order_data)

            except Exception as e:
                logger.exception(f"Error processing cleared order: {order}", exc_info=True)

        logger.info("Orders updated", extra={"order_count": len(orders)})

def process_cleared_markets(self, event):
    cleared_markets = event.event
    for cleared_market in cleared_markets:
        market_id = cleared_market.market_id
        market_info = {
            "market_id": market_id,
            "profit": cleared_market.profit,
            "commission": cleared_market.commission,
        }

        # Log the cleared market information
        logger.info(f"Processing cleared market: {market_id}")

        # Perform additional processing or logging if needed
        self._process_cleared_market(cleared_market)

    # Log the total number of cleared markets
    logger.info(
        "Cleared markets processed", extra={"cleared_market_count": len(cleared_markets)}
    )

def process_cleared_market():
    # Implement your custom logic for processing a single cleared market
    # For example, you can store the cleared market data in a database or perform other actions
    pass
