from textblob import TextBlob


def analyze_sentiment(text):
    """Analyze sentiment of text and return (score, label)."""
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 4)

    if polarity < -0.1:
        label = "Negative"
    elif polarity > 0.1:
        label = "Positive"
    else:
        label = "Neutral"

    return polarity, label
