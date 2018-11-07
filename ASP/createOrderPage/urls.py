from django.urls import path

from . import views

urlpatterns = [
    path('', views.createOrderPage),
    # path('./createOrderPage/', views.createOrderPage)
]