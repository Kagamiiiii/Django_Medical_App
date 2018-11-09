from django.urls import path

from . import views

urlpatterns = [
    path('main/', views.createOrderPage.as_view()),
    path('createOrder/', views.createOrderPage.as_view(), name='order'),
    path('view_detail/<int:pk>/', views.DetailView.as_view(), name='detail'),
]