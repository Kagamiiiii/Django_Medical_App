from django.urls import path

from . import views

urlpatterns = [
    path('', views.createOrderPage),
    path('createOrder/', views.createOrder)
]