from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from .models import Business
import requests

logger = get_task_logger(__name__)

@shared_task
def update_google_stats_for_all_businesses():
    qs = Business.objects.exclude(place_id__isnull=True).exclude(place_id="")
    logger.info("Updating %s businesses…", qs.count())

    headers = {
        "X-Goog-Api-Key": settings.GOOGLE_PLACES_SERVER_API_KEY,   # server key
        "X-Goog-FieldMask": "rating,userRatingCount",              # v1 field mask
    }

    for biz in qs:
        url = f"https://places.googleapis.com/v1/places/{biz.place_id}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            if resp.status_code == 200 and isinstance(data, dict):
                biz.rating = data.get("rating")
                biz.total_reviews = data.get("userRatingCount")
                biz.save(update_fields=["rating", "total_reviews"])
                logger.info("Updated %s (rating=%s, reviews=%s)", biz.name, biz.rating, biz.total_reviews)
            else:
                logger.error("HTTP %s for %s: %s", resp.status_code, biz.name, data)
        except Exception as e:
            logger.exception("Error updating %s: %s", biz.name, e)

@shared_task
def update_google_stats_for_one_business(business_id: int):
    biz = Business.objects.filter(id=business_id).exclude(place_id__isnull=True).exclude(place_id="").first()
    if not biz:
        return
    headers = {
        "X-Goog-Api-Key": settings.GOOGLE_PLACES_SERVER_API_KEY,
        "X-Goog-FieldMask": "rating,userRatingCount",
    }
    url = f"https://places.googleapis.com/v1/places/{biz.place_id}"
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json() if resp.ok else {}
    if resp.status_code == 200 and isinstance(data, dict):
        biz.rating = data.get("rating")
        biz.total_reviews = data.get("userRatingCount")
        biz.save(update_fields=["rating", "total_reviews"])