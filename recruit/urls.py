from django.urls import path

from recruit import views

app_name = "recruits"

urlpatterns = [
    path("", views.RecruitView.as_view(), name="index"),
    path("recruit/<int:pk>/like/", views.like_recruit, name="like_recruit"),
    path("recruit/<int:pk>/unlike/", views.unlike_recruit, name="unlike_recruit"),
    path(
        "recruits/<int:pk>/", views.RecruitDetailView.as_view(), name="recruit_detail"
    ),
    path(
        "recruits/<int:pk>/requests/",
        views.RequestView.as_view(),
        name="recruit_request",
    ),
    path(
        "registers/confirm/<int:pk>/",
        views.ConfirmRegisterView.as_view(),
        name="confirm_request",
    ),
    path(
        "registers/cancel/<int:pk>/",
        views.CancelRegisterView.as_view(),
        name="cancel_request",
    ),
    path("recruits/new/", views.RecruitCreateView.as_view(), name="create_recruit"),
    path(
        "recruits/<int:pk>/modify/",
        views.RecruitModifyView.as_view(),
        name="modify_recruit",
    ),
    path(
        "recruits/<int:pk>/delete/",
        views.RecruitDeleteView.as_view(),
        name="delete_recruit",
    ),
    path(
        "files/<int:file_pk>/delete/<int:recruit_pk>/",
        views.FileDeleteView.as_view(),
        name="file_delete",
    ),
    path(
        "recruits/<int:pk>/requests/<int:user_id>/reviews/",
        views.RequesterReviewView.as_view(),
        name="requester_review",
    ),
]
