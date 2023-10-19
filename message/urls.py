from django.urls import path

from . import views

app_name = "message"
urlpatterns = [
    path(
        "send/<int:user_id>/",
        views.MessageSendTargetView.as_view(),
        name="send_message_target",
    ),
    path("<int:pk>/read/", views.MessageReadView.as_view(), name="read_message"),
    path("<int:pk>/delete/", views.MessageDeleteView.as_view(), name="delete_message"),
    path("list/", views.MessageListView.as_view(), name="list_messages"),
    path("notices/", views.NoticeListView.as_view(), name="list_notices"),
    path(
        "notice/<int:pk>/delete/",
        views.NoticeDeleteView.as_view(),
        name="notice_delete",
    ),
]
