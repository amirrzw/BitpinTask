from django.urls import path
from .views import UserRegistrationView, CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh-token/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
