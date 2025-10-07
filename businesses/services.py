import requests
from django.conf import settings

def fetch_google_stats_for_place(place_id: str):
    """Returns (rating, user_rating_count) or (None, None) on failure."""
    if not place_id:
        return None, None
    headers = {
        "X-Goog-Api-Key": settings.GOOGLE_PLACES_SERVER_API_KEY,
        "X-Goog-FieldMask": "rating,userRatingCount",
    }
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    try:
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code != 200:
            return None, None
        data = resp.json() or {}
        return data.get("rating"), data.get("userRatingCount")
    except Exception:
        return None, None
