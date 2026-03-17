import re
from collections import Counter
from datetime import date

from flask import Blueprint, request, jsonify

from models.database import get_trend_data, get_heatmap_data, get_wordcloud_data, get_summary_data

analytics_bp = Blueprint("analytics", __name__)

STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which",
    "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by",
    "for", "with", "about", "against", "between", "through", "during", "before", "after",
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should",
    "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", "couldn", "didn", "doesn",
    "hadn", "hasn", "haven", "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn",
    "wasn", "weren", "won", "wouldn", "also", "really", "much", "got", "get", "like",
    "went", "going", "today", "day", "felt", "feeling", "feel", "lot", "bit", "still",
}


def _count_words(notes):
    counter = Counter()
    for note in notes:
        words = re.findall(r"[a-z']+", note.lower())
        for w in words:
            if w not in STOP_WORDS and len(w) > 1:
                counter[w] += 1
    return counter


@analytics_bp.route("/api/analytics/trends")
def trends():
    days_param = request.args.get("days", "30")
    days = None if days_param == "all" else int(days_param)

    data = get_trend_data(days=days)
    return jsonify({
        "dates": [d["entry_date"] for d in data],
        "mood_ratings": [d["mood_rating"] for d in data],
        "sentiment_scores": [d["sentiment_score"] for d in data],
        "notes": [d["note"] for d in data],
    })


@analytics_bp.route("/api/analytics/heatmap")
def heatmap():
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    data = get_heatmap_data(year, month)
    return jsonify(data)


@analytics_bp.route("/api/analytics/wordcloud")
def wordcloud():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    notes = get_wordcloud_data(start_date=start_date, end_date=end_date)
    counter = _count_words(notes)
    words = [{"text": word, "count": count} for word, count in counter.most_common(100)]
    return jsonify(words)


@analytics_bp.route("/api/analytics/summary")
def summary():
    entries = get_summary_data()

    if not entries:
        return jsonify({
            "has_data": False,
            "message": "No entries in the last 7 days.",
        })

    mood_ratings = [e["mood_rating"] for e in entries]
    sentiment_scores = [e["sentiment_score"] for e in entries]
    notes = [e["note"] for e in entries]

    avg_mood = round(sum(mood_ratings) / len(mood_ratings), 2)
    avg_sentiment = round(sum(sentiment_scores) / len(sentiment_scores), 4)

    best_idx = mood_ratings.index(max(mood_ratings))
    worst_idx = mood_ratings.index(min(mood_ratings))

    # Trend direction
    if len(mood_ratings) >= 2:
        first_half = mood_ratings[: len(mood_ratings) // 2]
        second_half = mood_ratings[len(mood_ratings) // 2:]
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        diff = avg_second - avg_first
        if diff > 0.3:
            trend = "improving"
        elif diff < -0.3:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # Top words
    counter = _count_words(notes)
    top_words = [w for w, _ in counter.most_common(5)]

    return jsonify({
        "has_data": True,
        "num_entries": len(entries),
        "avg_mood": avg_mood,
        "avg_sentiment": avg_sentiment,
        "best_day": {"date": entries[best_idx]["entry_date"], "mood": entries[best_idx]["mood_rating"]},
        "worst_day": {"date": entries[worst_idx]["entry_date"], "mood": entries[worst_idx]["mood_rating"]},
        "trend": trend,
        "top_words": top_words,
    })
