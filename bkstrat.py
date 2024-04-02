import pandas as pd
from flumine import BaseStrategy 
from flumine.order.trade import Trade
from flumine.order.order import LimitOrder
from flumine.markets.market import Market
from betfairlightweight.resources import MarketBook
import logging
import datetime
from flumine import events
import requests
from io import StringIO
import time

logger = logging.getLogger(__name__)
# Thoroughbred model (named the kash-ratings-model)
kash_url_1 = 'https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date='
kash_url_2 = pd.Timestamp.now().strftime("%Y-%m-%d") # todays date formatted as YYYY-mm-dd
kash_url_3 = '&amp;presenter=RatingsPresenter&amp;csv=true'

kash_url = kash_url_1 + kash_url_2 + kash_url_3

# Greyhounds model (named the iggy-joey-model)
iggy_url_1 = 'https://betfair-data-supplier-prod.herokuapp.com/api/widgets/iggy-joey/datasets?date='
iggy_url_2 = pd.Timestamp.now().strftime("%Y-%m-%d")
iggy_url_3 = '&amp;presenter=RatingsPresenter&amp;csv=true'

iggy_url = iggy_url_1 + iggy_url_2 + iggy_url_3

# Strategy for Thoroughbreds model
      
class FlatKashModel(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("starting strategy 'FlatKashModel'")
      
def download_csv(url, max_retries=3, retry_delay=1):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return pd.read_csv(StringIO(response.text))
        except (requests.exceptions.RequestException, pd.errors.ParserError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Error downloading CSV from {url}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to download CSV from {url} after {max_retries} attempts. Error: {e}")
                raise                 

    kash_df = download_csv(kash_url)
      
    def start(self, flumine) -> None:
        print("starting strategy 'FlatKashModel'")
        kash_url_1 = 'https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date='
        kash_url_2 = pd.Timestamp.now().strftime("%Y-%m-%d")
        kash_url_3 = '&amp;presenter=RatingsPresenter&amp;csv=true'
        kash_url = kash_url_1 + kash_url_2 + kash_url_3
        kash_df = pd.read_csv(kash_url)
        kash_df = kash_df.rename(columns={"meetings.races.bfExchangeMarketId":"market_id","meetings.races.runners.bfExchangeSelectionId":"selection_id","meetings.races.runners.ratedPrice":"rating"})
        kash_df = kash_df[['market_id','selection_id','rating']]
        kash_df['market_id'] = kash_df['market_id'].astype(str)
        self.kash_df = kash_df.set_index(['market_id','selection_id'])
    
    def check_market_book(self, market_book: MarketBook) -> bool:
        if market_book.status != "CLOSED":
            logger.info(f"Checking market {market_book.market_id}")
        return True

    def process_market_book(self, market: Market, market_book: MarketBook) -> None:
        try:
            if market.seconds_to_start < 60 and market_book.inplay == False:
                for runner in market_book.runners:
                    if runner.status == "ACTIVE" and runner.ex.available_to_back[0] and runner.ex.available_to_lay[0]:                     
                        if runner.ex.available_to_back[0]['price'] > self.kash_df.loc[market_book.market_id].loc[runner.selection_id].item():
                            logger.info(f"Placing back order for selection {runner.selection_id} in market {market_book.market_id}")
                        
                            trade = Trade(
                                market_id=market_book.market_id,
                                selection_id=runner.selection_id,
                                handicap=runner.handicap,
                                strategy=self,
                            )
                            order = trade.create_order(
                                side="BACK", order_type=LimitOrder(price=runner.ex.available_to_back[0]['price'], size=5.00)
                            )
                            market.place_order(order)
                        if runner.ex.available_to_lay[0]['price'] < self.kash_df.loc[market_book.market_id].loc[runner.selection_id].item():
                            logger.info(f"Placing lay order for selection {runner.selection_id} in market {market_book.market_id}")
                            
                            trade = Trade(
                                market_id=market_book.market_id,
                                selection_id=runner.selection_id,
                                handicap=runner.handicap,
                                strategy=self,
                            )
                            order = trade.create_order(
                                side="LAY", order_type=LimitOrder(price=runner.ex.available_to_lay[0]['price'], size=1.00)
                            )
                            market.place_order(order)
                        print(f"Processing market: {market.market_id}")
                    if not self.check_market_book(market_book):
                        return
        except Exception as e:
            # Log the exception or handle it as needed
            logger.error(f"An error occurred while processing the market book: {e}")

class FlatIggyModel(BaseStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("starting strategy 'FlatIggyModel'") 

def download_csv(url, max_retries=3, retry_delay=1):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return pd.read_csv(StringIO(response.text))
        except (requests.exceptions.RequestException, pd.errors.ParserError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Error downloading CSV from {url}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to download CSV from {url} after {max_retries} attempts. Error: {e}")
                raise

    iggy_df = download_csv(iggy_url)

    def start(self, flumine) -> None: 
        iggy_url_1 = 'https://betfair-data-supplier-prod.herokuapp.com/api/widgets/iggy-joey/datasets?date='
        iggy_url_2 = pd.Timestamp.now().strftime("%Y-%m-%d")
        iggy_url_3 = '&presenter=RatingsPresenter&csv=true'
        iggy_url = iggy_url_1 + iggy_url_2 + iggy_url_3
        iggy_df = pd.read_csv(iggy_url)
        iggy_df = iggy_df.rename(columns={"meetings.races.bfExchangeMarketId":"market_id","meetings.races.runners.bfExchangeSelectionId":"selection_id","meetings.races.runners.ratedPrice":"rating"})
        iggy_df = iggy_df[['market_id','selection_id','rating']]
        iggy_df['market_id'] = iggy_df['market_id'].astype(str)
        self.iggy_df = iggy_df.set_index(['market_id','selection_id'])
        
    def check_market_book(self, market_book: MarketBook) -> bool:
        if market_book.status != "CLOSED":
            market_book.log_control(events.MarketEvent(print(f"Processing market: {market_book.market_id}"), f"Checking market {market_book.market_id}"))
            return True

    def process_market_book(self, market: Market, market_book: MarketBook) -> None:
        if market.seconds_to_start < 60 and market_book.inplay == False:
            for runner in market_book.runners:
                if runner.status == "ACTIVE" and runner.ex.available_to_back[0] and runner.ex.available_to_lay[0]:                
                    if runner.ex.available_to_back[0]['price'] > self.iggy_df.loc[market_book.market_id].loc[runner.selection_id].item():
                        trade = Trade(
                            market_id=market_book.market_id,
                            selection_id=runner.selection_id,
                            handicap=runner.handicap,
                            strategy=self,
                        )
                        order = trade.create_order(
                            side="BACK", order_type=LimitOrder(price=runner.ex.available_to_back[0]['price'], size=1.00)
                        )
                        market.place_order(order)
                    if runner.ex.available_to_lay[0]['price'] < self.iggy_df.loc[market_book.market_id].loc[runner.selection_id].item():
                        trade = Trade(
                        market_id=market_book.market_id,
                        selection_id=runner.selection_id,
                        handicap=runner.handicap,
                        strategy=self,
                        )
                        order = trade.create_order(
                            side="LAY", order_type=LimitOrder(price=runner.ex.available_to_lay[0]['price'], size=1.00)
                        )
                        market.place_order(order)
                        
                        if not self.check_market_book(market_book):
                            print(f"Processing market: {market.market_id}")

def terminate(flumine, seconds_closed: int = 600) -> None:
    """
    Terminate the Flumine framework if no markets are live today or if all markets
    have been closed for a specified duration.

    :param flumine: The Flumine framework instance
    :param today_only: Flag to check markets for today only
    :param seconds_closed: Duration in seconds to check for market closure
    """
    # Get the list of markets from the Flumine framework
    markets = list(flumine.markets.markets.values())

    # Filter the markets based on the condition
    markets_today = [
        m
        for m in markets
        if m.market_start_datetime.date() == datetime.datetime.utcnow().date()
        and (
            m.elapsed_seconds_closed is None
            or (m.elapsed_seconds_closed and m.elapsed_seconds_closed < seconds_closed)
        )
    ]

logger = logging.getLogger(__name__)