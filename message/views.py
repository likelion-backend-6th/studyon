from django.shortcuts import render, redirect
from django.views.generic import View, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from manager.models import Study
from .models import Message, Notice


class NoticeListView(LoginRequiredMixin, ListView):
    model = Notice
    template_name = "messages/notice_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notices"] = Notice.objects.filter(user=self.request.user)
        return context


class NoticeDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        return redirect("message:list_notices")

    def post(self, reuqest, pk):
        notice = get_object_or_404(Notice, id=pk, user=reuqest.user)
        notice.delete()
        return redirect("message:list_notices")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "messages/message_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = Message.objects.filter(reciever=self.request.user)[:10]
        return context


class MessageSendView(LoginRequiredMixin, View):
    def get(self, request, study_id, user_id):
        reciever = get_object_or_404(User, id=user_id)
        study = get_object_or_404(Study, id=study_id)
        return render(
            request,
            "messages/send_message.html",
            {"reciever": reciever, "study": study},
        )

    def post(self, request, study_id, user_id):
        reciever = get_object_or_404(User, id=user_id)
        sender = request.user
        title = request.POST["title"]
        content = request.POST["content"]

        Message.objects.create(
            sender=sender, reciever=reciever, title=title, content=content
        )

        return redirect("manager:study_detail", study_id)


class MessageReadView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "messages/read_message.html"
    context_object_name = "message"

    def dispatch(self, request, *args, **kwargs):
        message = get_object_or_404(Message, id=kwargs["pk"])
        if message.reciever == request.user:
            message.read_at = timezone.now()
            message.save()
        return super().dispatch(request, *args, **kwargs)
