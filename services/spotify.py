import json
import time
import urllib.request
import urllib.parse
import base64

import config

MOOD_QUERIES = {
    1: "sad lofi",
    2: "melancholy acoustic",
    3: "chill ambient",
    4: "feel good pop",
    5: "upbeat happy dance",
}

_token_cache = {"token": None, "expires_at": 0}


def _get_access_token():
    """Get a Spotify access token using Client Credentials Flow, with in-memory caching."""
    if _token_cache["token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["token"]

    client_id = config.SPOTIFY_CLIENT_ID
    client_secret = config.SPOTIFY_CLIENT_SECRET
    if not client_id or not client_secret:
        return None

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()

    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read())

    _token_cache["token"] = body["access_token"]
    _token_cache["expires_at"] = time.time() + body.get("expires_in", 3600) - 60
    return _token_cache["token"]


def get_tracks_for_mood(mood, limit=5):
    """Search Spotify for tracks matching a mood (1-5). Returns a list of track dicts."""
    token = _get_access_token()
    if not token:
        return None

    query = MOOD_QUERIES.get(mood, "chill")
    params = urllib.parse.urlencode({"q": query, "type": "track", "limit": limit})
    url = f"https://api.spotify.com/v1/search?{params}"

    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})

    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read())

    tracks = []
    for item in body.get("tracks", {}).get("items", []):
        track_id = item["id"]
        album_images = item.get("album", {}).get("images", [])
        tracks.append({
            "name": item["name"],
            "artist": ", ".join(a["name"] for a in item.get("artists", [])),
            "spotify_url": item["external_urls"].get("spotify", ""),
            "embed_url": f"https://open.spotify.com/embed/track/{track_id}",
            "album_image": album_images[0]["url"] if album_images else "",
        })

    return tracks
