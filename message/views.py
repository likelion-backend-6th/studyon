from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from message.permissions import MessageAccessMixin, MessageSendMixin, NoticeAccessMixin
from .models import Message, Notice


class NoticeListView(LoginRequiredMixin, ListView):
    model = Notice
    template_name = "messages/notice_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notices"] = Notice.objects.filter(user=self.request.user)
        return context


class NoticeDeleteView(NoticeAccessMixin, View):
    def get(self, request, pk):
        return redirect("message:list_notices")

    def post(self, request, pk):
        notice = get_object_or_404(Notice, id=pk, user=request.user)
        notice.delete()
        return redirect("message:list_notices")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "messages/message_list.html"
    context_object_name = "messages"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(reciever=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        ...
        page = context["page_obj"]
        paginator = page.paginator
        pagelist = paginator.get_elided_page_range(
            page.number, on_each_side=3, on_ends=0
        )
        context["pagelist"] = pagelist
        ...
        return context


class MessageSendTargetView(MessageSendMixin, View):
    def get(self, request, user_id):
        reciever = get_object_or_404(User, id=user_id)
        return render(
            request,
            "messages/send_message_target.html",
            {"reciever": reciever},
        )

    def post(self, request, user_id):
        reciever = get_object_or_404(User, id=user_id)
        sender = request.user
        title = request.POST["title"]
        content = request.POST["content"]

        Message.objects.create(
            sender=sender, reciever=reciever, title=title, content=content
        )

        return redirect("message:list_messages")


class MessageReadView(MessageAccessMixin, DetailView):
    model = Message
    template_name = "messages/read_message.html"
    context_object_name = "message"

    def dispatch(self, request, *args, **kwargs):
        message = get_object_or_404(Message, id=kwargs["pk"])
        if message.reciever == request.user:
            message.read_at = timezone.now()
            message.save()
        return super().dispatch(request, *args, **kwargs)


class MessageDeleteView(MessageAccessMixin, View):
    def post(self, request, pk):
        message = get_object_or_404(Message, id=pk)

        try:
            message.delete()
            return redirect("message:list_messages")
        except Exception as e:
            return HttpResponse(str(e))
