from django.urls import path

from . import views


app_name = "manager"

urlpatterns = [
    path("", views.StudyView.as_view(), name="studies_list"),
    path("<int:pk>/", views.StudyDetailView.as_view(), name="study_detail"),
    path("<int:pk>/modify/", views.StudyModifyView.as_view(), name="study_modify"),
    path("<int:pk>/done", views.StudyDoneView.as_view(), name="study_done"),
    path("<int:pk>/finished", views.StudyFinishView.as_view(), name="study_finished"),
    path("<int:pk>/leave", views.StudyLeaveView.as_view(), name="study_leave"),
    path("<int:pk>/delete", views.StudyDeleteView.as_view(), name="study_delete"),
    path(
        "<int:study_id>/kickout/<int:member_id>/",
        views.StudyKickoutView.as_view(),
        name="study_kickout",
    ),
    path(
        "tasks/<int:pk>/modify/",
        views.TaskModifyView.as_view(),
        name="task_modify",
    ),
    path(
        "tasks/<int:pk>/complete/",
        views.TaskCompleteView.as_view(),
        name="task_complete",
    ),
    path(
        "tasks/<int:pk>/delete/",
        views.TaskDeleteView.as_view(),
        name="task_delete",
    ),
    path("tasks/<int:pk>/posts/new/", views.create_post_with_files, name="post_create"),
    path("tasks/<int:pk>/posts/", views.PostView.as_view(), name="post_list"),
    path("posts/<int:pk>/modify/", views.update_post_with_files, name="post_modify"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
]
