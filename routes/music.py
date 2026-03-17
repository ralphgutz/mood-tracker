from flask import Blueprint, request, jsonify

import config
from services.spotify import get_tracks_for_mood

music_bp = Blueprint("music", __name__)


@music_bp.route("/api/music")
def music():
    mood = request.args.get("mood", type=int)
    if mood is None or mood not in (1, 2, 3, 4, 5):
        return jsonify({"error": "mood query parameter is required and must be 1-5"}), 400

    if not config.SPOTIFY_CLIENT_ID or not config.SPOTIFY_CLIENT_SECRET:
        return jsonify({"error": "Spotify API credentials are not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."}), 503

    try:
        tracks = get_tracks_for_mood(mood, limit=5)
    except Exception:
        return jsonify({"error": "Failed to fetch tracks from Spotify"}), 502

    if tracks is None:
        return jsonify({"error": "Spotify API credentials are not configured."}), 503

    return jsonify(tracks)
