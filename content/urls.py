from django.urls import path
from .views import ContentListView, RatingCreateUpdateView

urlpatterns = [
    path('', ContentListView.as_view(), name='content_list'),
    path('<int:pk>/rate/', RatingCreateUpdateView.as_view(), name='rate_content'),
]
