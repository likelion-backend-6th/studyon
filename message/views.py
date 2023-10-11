from django.shortcuts import render, redirect
from django.views.generic import View, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
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
        study = get_object_or_404(Notice, id=pk, user=reuqest.user)
        study.delete()
        return redirect("message:list_notices")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "messages/message_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = Message.objects.filter(reciever=self.request.user)[:10]
        return context


class MessageSendView(LoginRequiredMixin, View):
    def get(self, request, pk):
        reciever = get_object_or_404(User, id=pk)
        return render(request, "messages/send_message.html", {"reciever": reciever})

    def post(self, request, pk):
        reciever = get_object_or_404(User, id=pk)
        sender = request.user
        title = request.POST["title"]
        content = request.POST["content"]

        Message.objects.create(
            sender=sender, reciever=reciever, title=title, content=content
        )

        return redirect("manager:studies_list")


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
