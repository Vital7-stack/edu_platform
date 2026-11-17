from rest_framework import permissions

MODERATORS_GROUP = 'moderators'


def is_moderator(user):
    return user.groups.filter(name=MODERATORS_GROUP).exists()


class IsModerator(permissions.BasePermission):
    """Доступ только для пользователей из группы модераторов."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_moderator(request.user))


class IsOwner(permissions.BasePermission):
    """Доступ на уровне объекта: только владелец."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsProfileOwner(permissions.BasePermission):
    """Профиль доступен только самому пользователю."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user