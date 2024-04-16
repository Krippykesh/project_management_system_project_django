from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.projects, name='projects'),
    path('new-task/', views.newTask, name='new-task'),
    path('new-project/', views.newProject, name='new-project'),
    path('update-project/', views.updateProject, name='update-project'),
]
