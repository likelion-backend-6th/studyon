from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    View,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages

from chat.forms import TagsForm
from chat.models import Room
from common.utils import InfiniteListView, s3_file_upload
from recruit.models import Recruit
from .models import File, Post, Study, Task
from .forms import (
    FileUploadFormSet,
    PostActionForm,
    StudyForm,
    TaskForm,
)
from .permissions import (
    FileManageMixin,
    PostAccessMixin,
    PostManageMixin,
    TaskAccessMixin,
    post_manage_permission,
    task_access_permission,
    StudyAccessMixin,
    StudyCreatorMixin,
    TaskAuthorMixin,
)


@login_required
def studies_like_recruit(request, pk):
    recruit = get_object_or_404(Recruit, pk=pk)
    if request.user.is_authenticated:
        recruit.like_users.add(request.user)
    return redirect("manager:studies_list")


@login_required()
def studies_unlike_recruit(request, pk):
    recruit = get_object_or_404(Recruit, pk=pk)
    if request.user.is_authenticated:
        recruit.like_users.remove(request.user)
    return redirect("manager:studies_list")


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


class StudyDetailView(StudyAccessMixin, DetailView):
    model = Study
    template_name = "studies/detail.html"
    context_object_name = "study"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.filter(study=self.object, is_active=True)
        if self.request.user in self.object.members.all():
            context["task_form"] = TaskForm()
            context["tags_form"] = TagsForm()
            context["room_list"] = list(
                Room.objects.filter(study=self.get_object()).values_list(
                    "id", "tags__name"
                )
            )
        return context


class StudyRecrutingView(StudyCreatorMixin, View):
    # url로 get 요청을 할경우 스터디 상세페이지 리디렉션
    def get(self, reqeust, pk):
        return redirect("manager:study_detail", pk)

    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk, is_active=True)
        # 요청유저와 스터디생성자가 같을 경우
        if request.user == study.creator:
            study.status = 1
            study.save()
            return redirect("manager:studies_list")
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", pk)


class StudyInProgressView(StudyCreatorMixin, View):
    # url로 get 요청을 할경우 스터디 상세페이지 리디렉션
    def get(self, reqeust, pk):
        return redirect("manager:study_detail", pk)

    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk, is_active=True)
        # 요청유저와 스터디생성자가 같을 경우
        if request.user == study.creator:
            study.status = 2
            study.save()
            return redirect("manager:studies_list")
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", pk)


class StudyDoneView(StudyCreatorMixin, View):
    # url로 get 요청을 할경우 스터디 상세페이지 리디렉션
    def get(self, reqeust, pk):
        return redirect("manager:study_detail", pk)

    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk, is_active=True)
        # 요청유저와 스터디생성자가 같을 경우
        if request.user == study.creator:
            study.status = 4
            study.save()
            return redirect("manager:studies_list")
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", pk)


class StudyFinishView(StudyCreatorMixin, View):
    # url로 get 요청을 할경우 스터디 상세페이지 리디렉션
    def get(self, reqeust, pk):
        return redirect("manager:study_detail", pk)

    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk, is_active=True)
        # 요청유저와 스터디생성자가 같을 경우
        if request.user == study.creator:
            study.status = 3
            study.save()
            return redirect("manager:studies_list")
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", pk)


class StudyLeaveView(StudyAccessMixin, View):
    # url로 get 요청을 할경우 스터디 목록페이지 리디렉션
    def get(self, reqeust, pk):
        return redirect("manager:studies_list")

    def post(self, request, pk):
        study = get_object_or_404(Study, id=pk, is_active=True)
        recruits = get_object_or_404(Recruit, study=study)
        # 요청유저가 스터디 멤버에 포함되어 있고 스터디장이 아닐 경우
        if request.user in study.members.all() and request.user != study.creator:
            study.members.remove(request.user)
            study.save()
            recruits.members.remove(request.user)
            recruits.save()
            return redirect("manager:studies_list")
        # 그 외 post 요청
        else:
            return redirect("manager:studies_list")


class StudyKickoutView(StudyCreatorMixin, View):
    # url로 get 요청을 할경우 스터디 상세페이지 리디렉션
    def get(self, reqeust, pk, member_id):
        return redirect("manager:study_detail", pk)

    def post(self, request, pk, member_id):
        user = get_object_or_404(User, id=member_id)
        study = get_object_or_404(Study, id=pk, is_active=True)
        recruit = get_object_or_404(Recruit, study=study)
        # 요청 유저가 스터디장이고 퇴출유저가 스터디 멤버에 포함되어 있을 경우
        if request.user == study.creator and user in study.members.all():
            study.members.remove(user)
            study.save()
            recruit.members.remove(user)
            recruit.save()
            return redirect("manager:study_detail", pk)
        else:
            return redirect("manager:study_detail", pk)


class StudyModifyView(StudyCreatorMixin, UpdateView):
    model = Study
    form_class = StudyForm
    template_name = "studies/modify.html"
    success_url = reverse_lazy("manager:study_detail")

    def dispatch(self, request, *args, **kwargs):
        # 요청유저와 스터디장이 다를 경우 스터디 상세페이지 리디렉션
        if request.user != self.get_object().creator:
            return redirect("manager:study_detail", self.get_object().id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("manager:study_detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study"] = get_object_or_404(Study, id=self.object.id, is_active=True)
        return context


class StudyDeleteView(StudyCreatorMixin, View):
    def get(self, request, pk):
        # url 로 get 요청을 보낼 경우 스터디 상세페이지 리디렉션
        return redirect("manager:study_detail", pk)

    def post(self, reuqest, pk):
        # 스터디의 is_active를 False 로 변경
        study = get_object_or_404(Study, id=pk, is_active=True)
        study.is_active = False
        study.save()
        return redirect("manager:studies_list")


class TaskCreateView(StudyAccessMixin, View):
    def get(self, request, pk):
        return redirect("manager:study_detail", pk)

    def post(self, request, pk):
        form = TaskForm(request.POST)
        study = get_object_or_404(Study, id=pk, is_active=True)
        # 폼이 유효하고 요청자가 스터디 멤버일 경우
        if form.is_valid() and request.user in study.members.all():
            task = form.save(commit=False)
            if task.start < task.end:
                task.study = study
                task.author = request.user
                task.save()
                return redirect("manager:study_detail", pk)
            else:
                messages.error(request, "Date form error")
                return redirect("manager:study_detail", pk)
        else:
            messages.error(request, "Form error")
            return redirect("manager:study_detail", pk)


class TaskModifyView(TaskAuthorMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "studies/tasks/modify.html"
    success_url = reverse_lazy("manager:study_detail")

    def get_success_url(self):
        return reverse("manager:study_detail", kwargs={"pk": self.object.study.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, id=self.object.id, is_active=True)
        return context


class TaskCompleteView(TaskAuthorMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk, is_active=True)
        return redirect("manager:study_detail", task.study.id)

    def post(self, request, pk):
        task = get_object_or_404(Task, id=pk, is_active=True)
        # 요청자가 task 생성자 일 경우
        if request.user == task.author:
            if task.is_finished:
                task.is_finished = False
            else:
                task.is_finished = True
            task.save()
            return redirect("manager:study_detail", task.study.id)
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", task.study.id)


class TaskDeleteView(TaskAuthorMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk, is_active=True)
        # url 로 get 요청을 보낼 경우 스터디 상세페이지 리디렉션
        return redirect("manager:study_detail", task.study.id)

    def post(self, request, pk):
        # task의 is_active를 False 로 변경
        task = get_object_or_404(Task, id=pk, is_active=True)
        # 요청자가 스터디 장이거나 task 생성자 일 경우
        if request.user == task.study.creator or request.user == task.author:
            task.is_active = False
            task.save()
            return redirect("manager:study_detail", task.study.id)
        # 그 외 post 요청
        else:
            return redirect("manager:study_detail", task.study.id)


class PostView(TaskAccessMixin, InfiniteListView):
    model = Post
    template_name = "studies/tasks/board.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        task_id = self.kwargs["pk"]
        queryset = Post.objects.filter(task_id=task_id)

        query = self.request.GET.get("query")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, id=self.kwargs["pk"])

        query = self.request.GET.get("query")
        if query:
            context["query"] = query
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
        file_upload_formset = FileUploadFormSet(request.POST, request.FILES)

        if post_form.is_valid() and file_upload_formset.is_valid():
            post_data = post_form.cleaned_data
            post = Post.objects.create(
                title=post_data["title"],
                task_id=pk,
                author=request.user,
                content=post_data["content"],
            )

            for file in file_upload_formset.files.values():
                name, url = s3_file_upload(file, "files")
                instance = File.objects.create(name=name, url=url)
                post.files.add(instance)

            post_list_url = reverse("manager:post_list", kwargs={"pk": pk})

            return redirect(post_list_url)
        else:
            for form in file_upload_formset:
                print(f"form.errors:{form.errors}")

    else:
        post_form = PostActionForm()
        file_upload_formset = FileUploadFormSet(queryset=File.objects.none())

    context = {
        "post_form": post_form,
        "file_upload_formset": file_upload_formset,
        "pk": pk,
    }

    return render(request, template_name, context)


@post_manage_permission
def update_post_with_files(request, pk):
    template_name = "studies/tasks/posts/action.html"

    post = get_object_or_404(Post, id=pk)
    task_id = post.task_id
    files = post.files.all()

    if request.method == "POST":
        post_form = PostActionForm(request.POST, instance=post)
        file_upload_formset = FileUploadFormSet(request.POST, request.FILES)

        if post_form.is_valid() and file_upload_formset.is_valid():
            post_form.save()

            for file in file_upload_formset.files.values():
                name, url = s3_file_upload(file, "files")
                instance = File.objects.create(name=name, url=url)
                post.files.add(instance)

            post_detail_url = reverse("manager:post_detail", kwargs={"pk": pk})

            return redirect(post_detail_url)
        else:
            for form in file_upload_formset:
                print(f"form.errors:{form.errors}")

    else:
        post_form = PostActionForm(instance=post)
        file_upload_formset = FileUploadFormSet(queryset=File.objects.none())

    context = {
        "post_form": post_form,
        "file_upload_formset": file_upload_formset,
        "files": files,
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


class FileDeleteView(FileManageMixin, View):
    def post(self, request, pk):
        file = get_object_or_404(File, id=pk)

        try:
            file.delete()
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponse(str(e))
