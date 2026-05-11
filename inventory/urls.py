from django.urls import path

from inventory import views

urlpatterns = [
    path('view_stock', views.view_stock, name='view_stock'),
    path('add_stock', views.add_stock, name='add_stock'),
    path('update_stock/<str:pk>/', views.update_stock, name='update_stock'),
    path('delete_stock/<str:pk>/', views.delete_stock, name='delete_stock'),
    path('stock_detail/<str:pk>/', views.stock_detail, name='stock_detail'),
    path('issue_item/<str:pk>/', views.issue_item, name='issue_item'),
    path('receive_item/<str:pk>/', views.receive_item, name='receive_item'),
    path('re_order/<str:pk>/', views.re_order, name='re_order'),
    path('view_history', views.view_history, name='view_history'),
]
