from rest_framework.throttling import UserRateThrottle

class RatingThrottle(UserRateThrottle):
    rate = '3/minute'
