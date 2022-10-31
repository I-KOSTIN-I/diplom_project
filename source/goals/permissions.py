from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from goals.models import BoardParticipant, Goal, GoalCategory, GoalComment


class BoardPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj
            ).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()


class GoalCategoryPermissions(IsAuthenticated):
    def has_object_permission(self, request, view, obj: GoalCategory):
        filters: dict = {'user': request.user, 'board': obj.board}
        if request.method in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class GoalPermissions(IsAuthenticated):
    def has_object_permission(self, request, view, obj: Goal):
        filters: dict = {'user': request.user, 'board': obj.category.board}
        if request.method in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class GoalCommentPermissions(IsAuthenticated):
    def has_object_permission(self, request, view, obj: GoalComment):
        return any((request.method in permissions.SAFE_METHODS or obj.user_id == request.user.id))
