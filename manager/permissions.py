from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import redirect

from manager.models import File, Post, Task, Study


# 스터디 멤버인지 확인
class StudyAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # 스터디에 포함되어 있지 않은 인원이 url 통해 들어올 경우 모집글로 리디렉션
        study = self.get_study()
        if request.user not in study.members.all():
            raise PermissionDenied("Not Authorized to Access")

        return super().dispatch(request, *args, **kwargs)

    def get_study(self):
        study_id = self.kwargs["pk"]
        study = get_object_or_404(Study, id=study_id)
        return study


# 스터디 장인지 확인
class StudyCreatorMixin(StudyAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        study = super().get_study()
        if request.user != study.creator:
            raise PermissionDenied("Not Authorized to Access")

        return super().dispatch(request, *args, **kwargs)


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


# Task 생성자인지 확인
class TaskAuthorMixin(TaskAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        task = super().get_task()
        if request.user != task.author:
            raise PermissionDenied("Not Authorized to Access")

        return super().dispatch(request, *args, **kwargs)


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


class FileManageMixin(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        file: File = self.get_file()
        if request.user != file.posts.first().author:
            raise PermissionDenied("Not Authorized to Access")

        return super().dispatch(request, *args, **kwargs)

    def get_file(self):
        file_id = self.kwargs["pk"]
        file: File = get_object_or_404(File, id=file_id)
        return file


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
