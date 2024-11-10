
import requests
import json
import pandas as pd
import time
from requests.exceptions import ConnectionError, Timeout
from sentiment_analysis.vader_sentiment import get_vader_sentiment
from sentiment_analysis.nlp_sentiment import get_nlp_sentiment
import numpy as np
from transformers import pipeline
import logging
import praw
from datetime import datetime, timedelta
logging.getLogger("transformers").setLevel(logging.ERROR)


# Reddit API setup using PRAW
reddit = praw.Reddit(
    client_id='WAul7vHV5lSNR0yA_U2J1Q',
    client_secret='5dxFATUF4gyM9Ln8DdpXF4BGIo7zvg',
    user_agent='windows:stock_sentiment_kafka_pipeline:v1.0 (by u/your_reddit_username)'
)

def fetch_reddit_sentiment(stock_symbol, start_day):
    outputs = {'Stock_symol': [], 'sentiment_score': 0, 'sentiment_score_nlp': 0,'time':''}  
    outputs['Stock_symol']= stock_symbol 
    liste1=[]
    liste2=[]                                                                                    
    try:
            subreddits_to_scrape = ['wallstreetbets', 'stocks', 'investing', 'StockMarket', 'ValueInvesting', 'Dividends', 'Daytrading']
            outputs['time']=start_day
           
            if isinstance(start_day, str):
              start_day = pd.Timestamp(start_day) 
            start_day = start_day.tz_localize('UTC')
        
            delay_threshold = start_day - pd.Timedelta(days=4)

            for subreddit_name in subreddits_to_scrape:
                subreddit = reddit.subreddit(subreddit_name)
                posts = subreddit.search(stock_symbol, limit=100, sort='new')  
                for post in posts:
                    time = pd.to_datetime(post.created_utc, unit='s', utc=True)
                    if time >= delay_threshold and time <= start_day :
                        
                        if stock_symbol.lower() in post.title.lower() or stock_symbol.lower() in post.selftext.lower():
                            time = pd.to_datetime(post.created_utc, unit='s').strftime('%Y-%m-%d')
                            # VADER Sentiment Analysis
                            summary = post.selftext[:1000]
                            title_sentiment = get_vader_sentiment(post.title)
                            body_sentiment = get_vader_sentiment(summary) if summary else 0
                            liste1.append(title_sentiment + body_sentiment)
                            
                            # NLP Sentiment Analysis (using Hugging Face)
                            if summary:
                                sentiment_label, sentiment_score_nlp = get_nlp_sentiment(summary)  # Use summary for NLP sentiment analysis
                                liste2.append(sentiment_score_nlp)
                            
                        # Average sentiment scores for the subreddit
            if liste1:
                sentiment_score = np.mean(liste1)
            else:
                sentiment_score = 0
                        
            if liste2:
                total_nlp_score = np.mean(liste2)
            else:
                total_nlp_score = 0

            outputs['sentiment_score'] = sentiment_score
            outputs['sentiment_score_nlp'] = total_nlp_score

    except Exception as e:
            print(f"Error fetching Reddit sentiment: {e}")

    return outputs