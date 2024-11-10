from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentiment_analysis.sentiment import adjust_sentiment_for_keywords

def get_vader_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    adjusted_score = adjust_sentiment_for_keywords(text, sentiment['compound'])
    return adjusted_score  
