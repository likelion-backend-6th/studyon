from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import redirect

from manager.models import Post, Task


class TaskAccessMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        task: Task = self.get_task()
        if request.user not in task.study.members.all():
            raise PermissionDenied("Not Authorized to Access")

        return super().dispatch(request, *args, **kwargs)

    def get_task(self):
        task_id = self.kwargs["pk"]
        task: Task = get_object_or_404(Task, id=task_id)
        return task


class PostAccessMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        post: Post = self.get_post()
        if request.user not in post.task.study.members.all():
            raise PermissionDenied("Not Authorized to Access")

        return super().dispatch(request, *args, **kwargs)

    def get_post(self):
        post_id = self.kwargs["pk"]
        post: Post = get_object_or_404(Post, id=post_id)
        return post


class PostManageMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        post: Post = self.get_post()
        if request.user != post.author:
            raise PermissionDenied("Not Authorized to Access")

        return super().dispatch(request, *args, **kwargs)

    def get_post(self):
        post_id = self.kwargs["pk"]
        post: Post = get_object_or_404(Post, id=post_id)
        return post


def task_access_permission(func):
    def permission_check(request: HttpRequest, pk):
        if request.user.is_anonymous:
            return redirect("users:login")

        task: Task = get_object_or_404(Task, id=pk)

        if request.user not in task.study.members.all():
            raise PermissionDenied("Not Authorized to Access")

        return func(request, pk)

    return permission_check


def post_manage_permission(func):
    def permission_check(request: HttpRequest, pk):
        if request.user.is_anonymous:
            return redirect("users:login")

        post: Post = get_object_or_404(Post, id=pk)

        if request.user != post.author:
            raise PermissionDenied("Not Authorized to Access")

        return func(request, pk)

    return permission_check
