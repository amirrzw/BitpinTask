from rest_framework import generics, permissions
from .models import Content
from .serializers import ContentSerializer, RatingSerializer
from .throttles import RatingThrottle

class ContentListView(generics.ListAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

class RatingCreateUpdateView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [RatingThrottle]

    def perform_create(self, serializer):
        content = generics.get_object_or_404(Content, id=self.kwargs['pk'])
        serializer.save(user=self.request.user, content=content)
