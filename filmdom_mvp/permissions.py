from rest_framework import permissions


class IsOwnerOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.creator == request.user


class CreationAllowed(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == "POST"


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class CreationAllowedIfAuthorized(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
