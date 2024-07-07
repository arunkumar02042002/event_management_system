from rest_framework.throttling import UserRateThrottle

class UnrestrictedThrottle(UserRateThrottle):
    scope = 'unrestricted'

class RestrictedThrottle(UserRateThrottle):
    scope = 'restricted'