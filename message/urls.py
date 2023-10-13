from django.urls import path

from . import views

app_name = "message"
urlpatterns = [
    path(
        "<int:study_id>/send/<int:user_id>",
        views.MessageSendView.as_view(),
        name="send_message",
    ),
    path("<int:pk>/read/", views.MessageReadView.as_view(), name="read_message"),
    path("list/", views.MessageListView.as_view(), name="list_messages"),
    path("notices/", views.NoticeListView.as_view(), name="list_notices"),
    path(
        "notice/<int:pk>/delete/",
        views.NoticeDeleteView.as_view(),
        name="notice_delete",
    ),
]
