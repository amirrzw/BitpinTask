from django.contrib import admin
from .models import Content, Rating

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'average_rating', 'ratings_count')
    search_fields = ('title', 'text')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'rating')
    list_filter = ('rating', 'content')
    search_fields = ('user__username', 'content__title')
