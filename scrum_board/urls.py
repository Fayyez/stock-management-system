from django.urls import path

from scrum_board import views

urlpatterns = [
    path('scrumboard', views.scrum_list, name='scrumboard'),
    path('scrumboard_view', views.scrum_view, name='scrumboard_view'),
]
