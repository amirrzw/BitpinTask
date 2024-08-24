from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache

class Content(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        cache_key = f'content_{self.id}_avg_rating'
        avg_rating = cache.get(cache_key)
        if avg_rating is None:
            avg_rating = self.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
            cache.set(cache_key, avg_rating)
        return avg_rating

    @property
    def ratings_count(self):
        cache_key = f'content_{self.id}_ratings_count'
        count = cache.get(cache_key)
        if count is None:
            count = self.ratings.count()
            cache.set(cache_key, count)
        return count

    def update_rating_in_cache(self, new_rating, previous_rating, is_new):
        cache_key_avg = f'content_{self.id}_avg_rating'
        cache_key_count = f'content_{self.id}_ratings_count'

        count = cache.get(cache_key_count) or 0
        avg_rating = cache.get(cache_key_avg) or 0

        if is_new:
            new_count = count + 1
            new_avg_rating = (avg_rating * count + new_rating) / new_count
        elif new_rating is not None:
            new_avg_rating = (avg_rating * count - previous_rating + new_rating) / count
            new_count = count
        else:
            if count > 1:
                new_count = count - 1
                new_avg_rating = (avg_rating * count - previous_rating) / new_count
            else:
                new_count = 0
                new_avg_rating = 0

        cache.set(cache_key_avg, new_avg_rating)
        cache.set(cache_key_count, new_count)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(6)])

    class Meta:
        unique_together = ('user', 'content')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_rating = None

        if not is_new:
            previous_rating = Rating.objects.get(pk=self.pk).rating

        super().save(*args, **kwargs)

        self.content.update_rating_in_cache(self.rating, previous_rating, is_new)

    def delete(self, *args, **kwargs):
        previous_rating = self.rating
        super().delete(*args, **kwargs)

        self.content.update_rating_in_cache(None, previous_rating, False)

    def __str__(self):
        return f'{self.user.username} rated {self.content.title} as {self.rating}'
