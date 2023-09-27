from django.urls import path

from . import views

app_name='manager'
urlpatterns = [
    path('', views.StudyView.as_view(), name='stuydies_list'),
]
