from django.urls import path

from . import views

app_name = 'ASP_webApp'

urlpatterns = [
    # --------------------------Register-----------------------------------
    # path('register/',),

    # --------------------------Clinic Manager-----------------------------
    path('CM/main/', views.CreateOrderPage.createOrderView, name='createOrderPage'),
    path('CM/main/createOrder/', views.CreateOrderPage.createOrder, name='createOrder'),
    path('CM/main/displayByCategory/', views.CreateOrderPage.displayByCategory, name='displayByCategory'),
    path('CM/main/displayByCategoryJson/', views.CreateOrderPage.displayByCategoryJson, name='displayByCategoryJson'),
    path('CM/main/orderAction/', views.CreateOrderPage.orderAction, name='orderCancel'),
    path('CM/main/viewOrder/', views.CreateOrderPage.viewOrder, name='viewOrder'),
    # --------------------------Dispatcher---------------------------------
    path('D/main', views.DispatchPage.dispatchView, name='dispatch'),
    path('D/dispatchUpdate/', views.DispatchPage.dispatchUpdate, name='dispatchUpdate'),
    path('D/createItinerary/', views.DispatchPage.createItinerary, name='dispatchItinerary'),
    # --------------------------Warehouse Personnel------------------------

]
