from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from common.utils import s3_file_upload
from recruit.models import Recruit
from .models import File, Post, Study, Task
from .forms import FileFormSet, FileUpdateForm, PostActionForm, StudyForm
from .permissions import (
    PostAccessMixin,
    PostManageMixin,
    TaskAccessMixin,
    post_manage_permission,
    task_access_permission,
)


class StudyView(LoginRequiredMixin, ListView):
    model = Study
    template_name = "studies/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_studies"] = Study.objects.filter(
            creator=self.request.user, is_active=True
        )
        context["in_studies"] = Study.objects.filter(
            members=self.request.user, is_active=True
        ).exclude(creator=self.request.user)
        context["my_recruits"] = Recruit.objects.filter(creator=self.request.user)
        context["like_recruits"] = Recruit.objects.filter(like_users=self.request.user)
        return context


class StudyDetailView(LoginRequiredMixin, DetailView):
    model = Study
    template_name = "studies/detail.html"
    context_object_name = "study"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.filter(study=self.object)
        return context


class StudyDoneView(LoginRequiredMixin, View):
    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk)
        study.status = 4
        study.save()
        return redirect("manager:studies_list")


class StudyFinishView(LoginRequiredMixin, View):
    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk)
        study.status = 3
        study.save()
        return redirect("manager:studies_list")


class StudyLeaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk)
        study.members.remove(request.user)
        study.save()
        return redirect("manager:studies_list")


class StudyKickoutView(LoginRequiredMixin, View):
    def post(self, request, study_id, member_id):
        user = get_object_or_404(User, id=member_id)
        study = get_object_or_404(Study, id=study_id)
        study.members.remove(user)
        study.save()
        return redirect("manager:study_detail", study_id)


class StudyModifyView(LoginRequiredMixin, UpdateView):
    model = Study
    form_class = StudyForm
    template_name = "studies/modify.html"
    success_url = reverse_lazy("manager:study_detail")

    def get_success_url(self):
        return reverse("manager:study_detail", kwargs={"pk": self.object.id})


class PostView(TaskAccessMixin, ListView):
    model = Post
    template_name = "studies/tasks/board.html"
    context_object_name = "posts"

    def get_queryset(self):
        task_id = self.kwargs["pk"]
        queryset = Post.objects.filter(task_id=task_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, id=self.kwargs["pk"])
        return context


class PostDetailView(PostAccessMixin, DetailView):
    model = Post
    template_name = "studies/tasks/posts/detail.html"
    context_object_name = "post"


@task_access_permission
def create_post_with_files(request, pk):
    template_name = "studies/tasks/posts/action.html"

    if request.method == "POST":
        post_form = PostActionForm(request.POST)
        file_formset = FileFormSet(request.POST, request.FILES)

        if post_form.is_valid() and file_formset.is_valid():
            post_data = post_form.cleaned_data
            post = Post.objects.create(
                title=post_data["title"],
                task_id=pk,
                author=request.user,
                content=post_data["content"],
            )

            for file in file_formset.files.values():
                url = s3_file_upload(file, "files")
                instance = File.objects.create(url=url)
                post.files.add(instance)

            post_list_url = reverse("manager:post_list", kwargs={"pk": pk})

            return redirect(post_list_url)
        else:
            for form in file_formset:
                print(f"form.errors:{form.errors}")

    else:
        post_form = PostActionForm()
        file_formset = FileFormSet(queryset=File.objects.none())

    context = {"post_form": post_form, "file_formset": file_formset, "pk": pk}

    return render(request, template_name, context)


@post_manage_permission
def update_post_with_files(request, pk):
    template_name = "studies/tasks/posts/action.html"

    post = get_object_or_404(Post, id=pk)
    task_id = post.task_id
    files = post.files.all()
    exist_file_cnt = files.count()
    min_file_form_cnt = 0 if files else 1
    FileFormSet = modelformset_factory(
        File, form=FileUpdateForm, extra=min_file_form_cnt
    )

    if request.method == "POST":
        post_form = PostActionForm(request.POST, instance=post)
        file_formset = FileFormSet(request.POST, request.FILES)

        if post_form.is_valid() and file_formset.is_valid():
            post_form.save()

            if exist_file_cnt:
                for i in range(exist_file_cnt):
                    if request.POST.getlist(f"form-{i}-checkbox") == ["on"]:
                        files[i].delete()

            for file in file_formset.files.values():
                url = s3_file_upload(file, "files")
                instance = File.objects.create(url=url)
                post.files.add(instance)

            post_list_url = reverse("manager:post_list", kwargs={"pk": task_id})

            return redirect(post_list_url)
        else:
            for form in file_formset:
                print(f"form.errors:{form.errors}")

    else:
        post_form = PostActionForm(instance=post)
        file_formset = FileFormSet(queryset=files)

    context = {
        "post_form": post_form,
        "file_formset": file_formset,
        "pk": pk,
        "task_id": task_id,
    }

    return render(request, template_name, context)


class PostDeleteView(PostManageMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, id=pk)

        try:
            post.delete()
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponse(str(e))
