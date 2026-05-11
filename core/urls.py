from django.urls import path

from core import views

urlpatterns = [
    path('', views.get_client_ip, name='home'),
    path('register', views.new_register, name='register'),
    path('dependent_forms', views.dependent_forms, name='dependent_forms'),
    path('dependent_update/<str:pk>/', views.dependent_forms_update, name='dependent_update'),
    path('depend_form_view', views.dependent_forms_view, name='depend_form_view'),
    path('depend_form_delete/<str:pk>', views.delete_dependant, name='delete_dependant'),
    path('ajax/load-states/', views.load_stats, name='ajax_load_states'),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    path('contacts', views.contact, name='contacts'),
]
