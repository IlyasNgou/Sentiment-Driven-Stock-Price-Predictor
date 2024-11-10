positive_keywords = ['going high', 'buy', 'invest', 'take the risk', 'good future']
negative_keywords = ['going down', 'no future', 'not invest', 'not worth', 'bad investment']

def adjust_sentiment_for_keywords(text, sentiment_score):
    lower_text = text.lower()

    # Adjust for positive phrases
    for keyword in positive_keywords:
        if keyword in lower_text:
            if 'not' in lower_text or "don't" in lower_text:
                sentiment_score -= 0.2  
            else:
                sentiment_score += 0.2  

    # Adjust for negative phrases
    for keyword in negative_keywords:
        if keyword in lower_text:
            if 'not' in lower_text or "don't" in lower_text:
                sentiment_score += 0.2 
            else:
                sentiment_score -= 0.2 

    return sentiment_score