from rest_framework import serializers
from .models import Content, Rating

class ContentSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    ratings_count = serializers.IntegerField(read_only=True)
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'title', 'text', 'average_rating', 'ratings_count', 'user_rating']

    def get_user_rating(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            rating = Rating.objects.filter(content=obj, user=user).first()
            return rating.rating if rating else None
        return None

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rating']

    def create(self, validated_data):
        user = self.context['request'].user
        content = self.context['content']
        rating, created = Rating.objects.update_or_create(
            user=user,
            content=content,
            defaults={'rating': validated_data['rating']}
        )
        return rating
