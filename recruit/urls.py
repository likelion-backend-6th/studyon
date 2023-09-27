from django.urls import path

from recruit import views

app_name = 'recruit'

urlpatterns = [
    path('', views.RecruitView.as_view(), name='index'),
]