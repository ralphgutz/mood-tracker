from datetime import date

from flask import Blueprint, request, jsonify

from models.database import (
    create_entry, get_entry, get_entry_by_date, list_entries, update_entry, delete_entry,
)
from services.sentiment import analyze_sentiment

entries_bp = Blueprint("entries", __name__)

MOOD_LABELS = {1: "Very Bad", 2: "Bad", 3: "Neutral", 4: "Good", 5: "Very Good"}


@entries_bp.route("/api/entries", methods=["POST"])
def create():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    mood = data.get("mood")
    note = data.get("note", "").strip()
    entry_date = data.get("date", date.today().isoformat())

    if mood is None or mood not in (1, 2, 3, 4, 5):
        return jsonify({"error": "mood must be an integer 1-5"}), 400
    if not note or len(note) > 500:
        return jsonify({"error": "note is required (1-500 characters)"}), 400

    existing = get_entry_by_date(entry_date)
    if existing:
        return jsonify({"error": "An entry already exists for this date. Use PUT to update."}), 409

    score, label = analyze_sentiment(note)
    entry = create_entry(mood, note, score, label, entry_date)
    return jsonify(entry), 201


@entries_bp.route("/api/entries", methods=["GET"])
def list_all():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    entries = list_entries(start_date=start_date, end_date=end_date, limit=limit, offset=offset)
    return jsonify(entries)


@entries_bp.route("/api/entries/<int:entry_id>", methods=["GET"])
def get_one(entry_id):
    entry = get_entry(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    return jsonify(entry)


@entries_bp.route("/api/entries/<int:entry_id>", methods=["PUT"])
def update(entry_id):
    entry = get_entry(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    mood = data.get("mood", entry["mood_rating"])
    note = data.get("note", entry["note"]).strip()

    if mood not in (1, 2, 3, 4, 5):
        return jsonify({"error": "mood must be an integer 1-5"}), 400
    if not note or len(note) > 500:
        return jsonify({"error": "note is required (1-500 characters)"}), 400

    score, label = analyze_sentiment(note)
    updated = update_entry(entry_id, mood, note, score, label)
    return jsonify(updated)


@entries_bp.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def delete(entry_id):
    entry = get_entry(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    delete_entry(entry_id)
    return jsonify({"message": "Entry deleted"}), 200
