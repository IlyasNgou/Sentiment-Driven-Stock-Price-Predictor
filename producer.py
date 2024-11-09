from confluent_kafka import Producer
import requests
import pandas as pd 
import json
import praw
import time
from requests.exceptions import ConnectionError, Timeout
from sentiment_analysis.vader_sentiment import get_vader_sentiment
from sentiment_analysis.nlp_sentiment import get_nlp_sentiment
from sentiment_analysis.fetch_sentiment import fetch_reddit_sentiment

# Set up Kafka Producer
producer_conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(**producer_conf)

# Alpha Vantage API setup
ALPHA_VANTAGE_API_KEY = 'D38KV9LTL0MV5XPO'
ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey=' + ALPHA_VANTAGE_API_KEY

# Function to fetch stock data from Alpha Vantage API with retry logic
def fetch_stock_data(symbol, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(ALPHA_VANTAGE_URL.format(symbol=symbol), timeout=10)
            response.raise_for_status()
            print(f"Successfully fetched stock data for {symbol}")
            return response.json()
        except (ConnectionError, Timeout) as e:
            print(f"Error fetching stock data for {symbol}: {e}. Retrying...")
            time.sleep(5)  # Wait before retrying
        except requests.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            break
    print(f"Failed to fetch stock data for {symbol} after {retries} attempts.")
    return None


# Function to produce messages to Kafka
def produce_data(symbol):
    stock_data = fetch_stock_data(symbol)
    counter=0
    if stock_data and 'Time Series (Daily)' in stock_data:
        for timestamp, data in stock_data['Time Series (Daily)'].items():
            latest_date = pd.to_datetime(timestamp).strftime('%Y-%m-%d')

            reddit_sentiment = fetch_reddit_sentiment(symbol, timestamp)

            sentiment_score = reddit_sentiment['sentiment_score']
            sentiment_score_nlp = reddit_sentiment['sentiment_score_nlp']

            message = {
                'symbol': symbol,
                'timestamp': timestamp,
                'open': data['1. open'],
                'high': data['2. high'],
                'low': data['3. low'],
                'close': data['4. close'],
                'volume': data['5. volume'],
                'sentiment_score': sentiment_score,
                'sentiment_score_nlp': sentiment_score_nlp,
            }

            try:
                # Produce message for each timestamp
                producer.produce('alpha_vantage_data', key=timestamp, value=json.dumps(message))
                producer.flush()
                print(f"Successfully produced message to Kafka for {symbol} at {timestamp}")
                time.sleep(1)  # simulate delay (same as the original code)
            except Exception as e:
                print(f"Error producing message to Kafka: {e}")
            counter += 1
            if counter >= 120:
                break
    else:
        print(f"Stock data for {symbol} is missing or incomplete.")
        
        
if __name__ == '__main__':
    stock_symbols = ['AAPL', 'TSLA', 'GOOGL']  #'MSFT''META','COMP','GOOGL','IBM',
    try:
        while True:
            for symbol in stock_symbols:
                print(f"\nProcessing {symbol}...")
                produce_data(symbol)
                time.sleep(5)  
    except KeyboardInterrupt:
        print("Stopped producing.")





# import requests
# from confluent_kafka import Producer
# import json
# import time

# # Kafka Producer configuration
# conf = {'bootstrap.servers': 'localhost:9092'}
# producer = Producer(**conf)

# # Alpha Vantage API details
# api_key = 'X4IQ127ELWY7IV84'
# symbols = ['AAPL', 'GOOGL', 'MSFT']  # List of stock symbols to fetch

# def delivery_report(err, msg):
#     """ Called once for each message produced to indicate delivery result. """
#     if err is not None:
#         print('Message delivery failed: {}'.format(err))
#     else:
#         print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

# def fetch_data(symbol):
#     """Fetch stock data for the given symbol and produce it to Kafka."""
#     api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}'
#     response = requests.get(api_url)
    
#     if response.status_code == 200:
#         data = response.json().get('Time Series (1min)', {})
#         for timestamp, values in data.items():
#             # Add the stock symbol to the message payload
#             message = {'symbol': symbol, 'timestamp': timestamp, **values}
#             producer.produce('alpha_vantage_data', key=timestamp, value=json.dumps(message), callback=delivery_report)
#             producer.flush()
#             time.sleep(1)  # simulate delay
#     else:
#         print(f"Failed to fetch data for {symbol}: {response.status_code}")

# if __name__ == '__main__':
#     for symbol in symbols:
#         fetch_data(symbol)
