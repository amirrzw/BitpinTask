from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .models import Content, Rating

logger = get_task_logger(__name__)

@shared_task
def recalculate_ratings():
    logger.info("Task started: recalculating ratings...")

    time_window = timedelta(minutes=15)
    rating_threshold = 50
    deviation_threshold = 1.5

    for content in Content.objects.all():
        now = timezone.now()
        recent_ratings = Rating.objects.filter(content=content, timestamp__gte=now - time_window)
        recent_count = recent_ratings.count()

        weights_cache_key = f'content_{content.id}_weights'
        weights = cache.get(weights_cache_key, {})

        if recent_count > 0:
            recent_avg = recent_ratings.aggregate(models.Avg('rating'))['rating__avg']

            historical_avg = content.average_rating
            if content.ratings_count > recent_count:
                overall_avg_without_recent = (
                    (historical_avg * content.ratings_count) - (recent_avg * recent_count)
                ) / (content.ratings_count - recent_count)
            else:
                overall_avg_without_recent = historical_avg

            if (recent_count > rating_threshold and
                abs(recent_avg - overall_avg_without_recent) > deviation_threshold):
                logger.info(f"Anomaly detected for content {content.id}: High rating activity with significant deviation.")
                for rating in recent_ratings:
                    weights[rating.id] = 0.5
            else:
                for rating in recent_ratings:
                    if rating.id not in weights:
                        weights[rating.id] = 1
        else:
            for rating_id in list(weights.keys()):
                if Rating.objects.filter(id=rating_id, timestamp__gte=now - time_window).exists():
                    continue
                del weights[rating_id]

        cache.set(weights_cache_key, weights)

        all_ratings = Rating.objects.filter(content=content)
        total_weighted_score = sum(rating.rating * weights.get(rating.id, 1) for rating in all_ratings)
        total_weight = sum(weights.get(rating.id, 1) for rating in all_ratings)

        if total_weight > 0:
            weighted_avg_rating = total_weighted_score / total_weight
        else:
            weighted_avg_rating = content.average_rating  # Fallback to existing average

        cache.set(f'content_{content.id}_avg_rating', weighted_avg_rating)
        cache.set(f'content_{content.id}_ratings_count', content.ratings.count())

        logger.info(f"Updated rating for content {content.id}: {weighted_avg_rating}")

    logger.info("Task completed: recalculating ratings.")
