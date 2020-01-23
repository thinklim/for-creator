from rest_framework import permissions
from blog.models import Blog


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """ obj is model which have a 'blog' attribute
        example: category, post, tag ... """

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.blog ==  Blog.objects.get(user=request.user) or request.user.is_superuser