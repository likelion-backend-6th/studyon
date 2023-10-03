from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    View,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from common.utils import s3_file_upload
from recruit.models import Recruit
from .models import File, Post, Study, Task
from .forms import FileFormSet, FileUpdateForm, PostActionForm, StudyForm, TaskForm
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
    login_url = "users:login"

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
    login_url = "users:login"

    def dispatch(self, request, *args, **kwargs):
        # 스터디에 포함되어 있지 않은 인원이 url 통해 들어올 경우 모집글로 리디렉션
        if request.user not in self.get_object().members.all():
            return redirect("recruits:recruit_detail", self.get_object().recruits.id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.filter(study=self.object)
        return context


class StudyDoneView(LoginRequiredMixin, View):
    login_url = "users:login"

    # url로 get 요청을 할경우 스터디 상세페이지 리디렉션
    def get(self, reqeust, pk):
        return redirect("manager:study_detail", pk)

    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk)
        # 요청유저와 스터디생성자가 같을 경우
        if request.user == study.creator:
            study.status = 4
            study.save()
            return redirect("manager:studies_list")
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", pk)


class StudyFinishView(LoginRequiredMixin, View):
    login_url = "users:login"

    # url로 get 요청을 할경우 스터디 상세페이지 리디렉션
    def get(self, reqeust, pk):
        return redirect("manager:study_detail", pk)

    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk)
        # 요청유저와 스터디생성자가 같을 경우
        if request.user == study.creator:
            study.status = 3
            study.save()
            return redirect("manager:studies_list")
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", pk)


class StudyLeaveView(LoginRequiredMixin, View):
    login_url = "users:login"

    # url로 get 요청을 할경우 스터디 목록페이지 리디렉션
    def get(self, reqeust, pk):
        return redirect("manager:studies_list")

    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk)
        # 요청유저가 스터디 멤버에 포함되어 있고 스터디장이 아닐 경우
        if request.user in study.members.all() and request.user != study.creator:
            study.members.remove(request.user)
            study.save()
            return redirect("manager:studies_list")
        # 그 외 post 요청
        else:
            return redirect("manager:studies_list")


class StudyKickoutView(LoginRequiredMixin, View):
    login_url = "users:login"

    # url로 get 요청을 할경우 스터디 상세페이지 리디렉션
    def get(self, reqeust, study_id, member_id):
        return redirect("manager:study_detail", study_id)

    def post(self, request, study_id, member_id):
        user = get_object_or_404(User, id=member_id)
        study = get_object_or_404(Study, id=study_id)
        # 요청 유저가 스터디장이고 퇴출유저가 스터디 멤버에 포함되어 있을 경우
        if request.user == study.creator and user in study.members.all():
            study.members.remove(user)
            study.save()
            return redirect("manager:study_detail", study_id)
        else:
            return redirect("manager:study_detail", study_id)


class StudyModifyView(LoginRequiredMixin, UpdateView):
    model = Study
    form_class = StudyForm
    template_name = "studies/modify.html"
    success_url = reverse_lazy("manager:study_detail")
    login_url = "users:login"

    def dispatch(self, request, *args, **kwargs):
        # 요청유저와 스터디장이 다를 경우 스터디 상세페이지 리디렉션
        if request.user != self.get_object().creator:
            return redirect("manager:study_detail", self.get_object().id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("manager:study_detail", kwargs={"pk": self.object.id})


class StudyDeleteView(LoginRequiredMixin, DeleteView):
    model = Study
    template_name = "studies/delete.html"
    success_url = reverse_lazy("manager:studies_list")
    login_url = "users:login"

    def dispatch(self, request, *args, **kwargs):
        # 요청유저와 스터디장이 다를 경우 스터디 상세페이지 리디렉션
        if request.user != self.get_object().creator:
            return redirect("manager:studies_list")
        return super().dispatch(request, *args, **kwargs)


class TaskCreateView(LoginRequiredMixin, View):
    login_url = "users:login"

    def get(self, request, study_id):
        study = get_object_or_404(Study, id=study_id)
        if request.user in study.members.all():
            form = TaskForm()
            return render(request, "studies/tasks/create.html", {"form": form})
        else:
            return redirect("manager:study_detail", study_id)

    def post(self, request, study_id):
        form = TaskForm(request.POST)
        study = get_object_or_404(Study, id=study_id)
        # 폼이 유효하고 요청자가 스터디 멤버일 경우
        if form.is_valid() and request.user in study.members.all():
            task = form.save(commit=False)
            task.study = study
            task.author = request.user
            task.save()
            return redirect("manager:study_detail", study_id)
        else:
            form = TaskForm()
            return render(request, "studies/tasks/create.html", {"form": form})


class TaskModifyView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "studies/tasks/modify.html"
    success_url = reverse_lazy("manager:study_detail")
    login_url = "users:login"

    def dispatch(self, request, *args, **kwargs):
        # 요청유저가 스터디멤버에 없거나 task 생성자가 아닌 경우
        if (
            request.user not in self.get_object().study.members.all()
            or request.user != self.get_object().creaotr
        ):
            return redirect("manager:study_detail", self.get_object().id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("manager:study_detail", kwargs={"pk": self.object.study.id})


class TaskCompleteView(LoginRequiredMixin, View):
    login_url = "users:login"

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        return redirect("manager:study_detail", task.study.id)

    def post(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        # 요청자가 스터디 장이거나 task 생성자 일 경우
        if request.user == task.study.creator or request.user == task.author:
            if task.is_finished:
                task.is_finished = False
            else:
                task.is_finished = True
            task.save()
            return redirect("manager:study_detail", task.study.id)
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", task.study.id)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "studies/tasks/delete.html"
    success_url = reverse_lazy("manager:study_detail")
    login_url = "users:login"

    def dispatch(self, request, *args, **kwargs):
        # 요청 유저가 스터디장이 아니거나 task 생성자가 아닐 경우
        if (
            request.user != self.get_object().study.creator
            or request.user != self.get_object.author
        ):
            return redirect("manager:study_detail", self.get_object().study.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("manager:study_detail", kwargs={"pk": self.object.study.id})


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
