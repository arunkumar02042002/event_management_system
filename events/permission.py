from rest_framework.permissions import BasePermission
from authentication.choices import UserTypeChoices

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class IsOrganizerOrReadOnly(BasePermission):
    """
    The request is authenticated as a organizer or admin, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.role in {UserTypeChoices.ORGANIZER, UserTypeChoices.ADMIN}
        )

class IsParticipantorEventOrganizer(BasePermission):
    """
    The request is authenticated as the event owner, or is a read-only request
    """

    def has_object_permission(self, request, view, obj):
        result = bool(
            request.method in SAFE_METHODS or
            (request.user and
            request.user == obj.created_by)
        )
        return result