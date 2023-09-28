from django.urls import path

from . import views

app_name='manager'
urlpatterns = [
    path('', views.StudyView.as_view(), name='studies_list'),
    path('<int:pk>/', views.StudyDetailView.as_view(), name='study_detail'),
]
