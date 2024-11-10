from transformers import pipeline

def summarize_text(text):
    summarizer = pipeline('summarization', framework='tf')  
    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
    return summary

def get_nlp_sentiment(text):
    classifier = pipeline('sentiment-analysis', model="distilbert-base-uncased-finetuned-sst-2-english", framework='tf')  
    if len(text.split()) > 512:
        text = summarize_text(text)
    sentiment = classifier(text)[0]
    return sentiment['label'], sentiment['score']
