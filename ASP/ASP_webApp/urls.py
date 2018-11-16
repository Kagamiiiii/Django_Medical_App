from django.urls import path

from . import views

app_name = 'ASP_webApp'

urlpatterns = [
    # --------------------------Register-----------------------------------
    # path('register/',),

    # --------------------------Clinic Manager-----------------------------
    path('CM/main/', views.createOrderPage.as_view()),
    path('CM/main/displayByCategory/', views.createOrderPage.displayByCategory, name='displayByCategory'),
    path('CM/main/displayByCategoryJson/', views.createOrderPage.displayByCategoryJson, name='displayByCategoryJson'),
    path('CM/main/createOrder/', views.createOrderPage.as_view(), name='createOrder'),
    path('CM/main/viewOrder/', views.createOrderPage.viewOrder, name='viewOrder'),
    path('CM/main/orderAction/', views.createOrderPage.orderAction, name='orderCancel'),
    # --------------------------Dispatcher---------------------------------
    path('D/main', views.dispatchView, name='dispatch'),
    path('D/dispatchUpdate/', views.dispatchUpdate, name='dispatch_update'),

    # --------------------------Warehouse Personnel------------------------

]
