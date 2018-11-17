from django.urls import path

from . import views

app_name = 'ASP_webApp'

urlpatterns = [
    # --------------------------Register-----------------------------------
    # path('register/',),

    # --------------------------Clinic Manager-----------------------------
    path('CM/main/', views.CreateOrderPage.createOrderView, name='createOrderPage'),
    path('CM/main/displayByCategory/', views.CreateOrderPage.displayByCategory, name='displayByCategory'),
    path('CM/main/displayByCategoryJson/', views.CreateOrderPage.displayByCategoryJson, name='displayByCategoryJson'),
    path('CM/main/createOrder/', views.CreateOrderPage.createOrder, name='createOrder'),
    path('CM/main/viewOrder/', views.CreateOrderPage.viewOrder, name='viewOrder'),
    path('CM/main/orderAction/', views.CreateOrderPage.orderAction, name='orderCancel'),
    # --------------------------Dispatcher---------------------------------
    path('D/main/', views.DispatchPage.dispatchView, name='dispatchPage'),
    path('D/main/dispatchDetail/', views.DispatchPage.dispatchViewDetail, name='dispatchPageDetail'),
    path('D/main/dispatchUpdate/', views.DispatchPage.dispatchUpdate, name='dispatchUpdate'),
    path('D/main/createItinerary/', views.DispatchPage.createItinerary, name='dispatchItinerary'),
    # --------------------------Warehouse Personnel------------------------
    path('WHP/main/', views.warehousePage.warehouseView, name='whpPage'),
    path('WHP/main/processOrder/', views.warehousePage.orderProcess, name='whpProcessOrder'),
    path('WHP/main/PDF/', views.warehousePage.getShippingLabel, name='whpPDF'),
]
