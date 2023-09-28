from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from recruit.models import Recruit
from .models import Post, Study, Task


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
        study = get_object_or_404(Study,id=pk)
        study.status = 4
        study.save()
        return redirect('manager:studies_list')

class StudyFinishView(LoginRequiredMixin, View):
    def post(self, request, pk):
        study = get_object_or_404(Study,id=pk)
        study.status = 3
        study.save()
        return redirect('manager:studies_list')
    
class StudyLeaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        study = get_object_or_404(Study,id=pk)
        study.members.remove(request.user)
        study.save()
        return redirect('manager:studies_list')
    
class StudyKickoutView(LoginRequiredMixin, View):
    def post(self, request, study_id, member_id):
        user = get_object_or_404(User, id=member_id)
        study = get_object_or_404(Study, id=study_id)
        study.members.remove(user)
        study.save()
        return redirect('manager:study_detail', study_id)
        


class PostView(LoginRequiredMixin, ListView):
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
