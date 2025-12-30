from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Разрешает доступ только администраторам"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsManagerOrAdmin(permissions.BasePermission):
    """Разрешает доступ менеджерам и администраторам"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager


class IsProjectMemberOrAdmin(permissions.BasePermission):
    """Разрешает доступ участникам проекта или администраторам"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return request.user in obj.members.all() or request.user == obj.creator


class IsTaskAssigneeOrAdmin(permissions.BasePermission):
    """Разрешает доступ исполнителю задачи или администраторам"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return request.user == obj.assigned_to
