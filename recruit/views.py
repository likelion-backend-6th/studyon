from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView

from recruit.forms import SearchForm, ApplicationForm
from recruit.models import Recruit, Register


# Create your views here.
class RecruitView(ListView):
    model = Recruit
    template_name = "recruits/index.html"
    context_object_name = "recruits"

    def get_queryset(self):
        queryset = Recruit.objects.all()
        query = self.request.GET.get("query")
        tag = self.request.GET.get("tag")

        if query:
            queryset = queryset.filter(title__icontains=query)

        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm()
        if self.request.user.is_authenticated:
            context["in_studies"] = Recruit.objects.filter(
                study__members=self.request.user
            )
            context["liked_studies"] = Recruit.objects.filter(
                like_users=self.request.user
            )
        else:
            context["in_studies"] = None
            context["liked_studies"] = None
        return context


def like_recruit(request, pk):
    recruit = get_object_or_404(Recruit, pk=pk)
    if request.user.is_authenticated:
        recruit.like_users.add(request.user)
    return redirect("recruits:index")


def unlike_recruit(request, pk):
    recruit = get_object_or_404(Recruit, pk=pk)
    if request.user.is_authenticated:
        recruit.like_users.remove(request.user)
    return redirect("recruits:index")


class RecruitDetailView(DetailView):
    model = Recruit
    template_name = "recruits/detail.html"
    context_object_name = "recruit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ApplicationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ApplicationForm(request.POST)
        recruit = self.get_object()
        if Register.objects.filter(recruit=recruit, requester=request.user).exists():
            messages.error(request, "이미 신청하셨습니다.")
            return redirect("recruits:recruit_detail", recruit.id)
        if form.is_valid():
            register = form.save(commit=False)
            register.recruit = self.get_object()
            register.requester = request.user
            register.save()
            return redirect("recruits:index")
        else:
            return self.render_to_response(self.get_context_data(form=form))


class RequestView(ListView):
    model = Register
    template_name = "recruits/requests.html"
    context_object_name = "registers"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(recruit__creator=self.request.user, is_joined=None)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ConfirmRegisterView(View):
    def post(self, request, *args, **kwargs):
        register = Register.objects.get(pk=kwargs["pk"])
        register.is_joined = True
        register.save()
        recruit = register.recruit
        recruit.members.add(register.requester)
        recruit.save()
        return redirect(
            reverse_lazy("recruits:recruit_request", args=[register.recruit.id])
        )


class CancelRegisterView(View):
    def post(self, request, *args, **kwargs):
        register = Register.objects.get(pk=kwargs["pk"])
        register.is_joined = False
        register.save()
        return redirect(
            reverse_lazy("recruits:recruit_request", args=[register.recruit.id])
        )
