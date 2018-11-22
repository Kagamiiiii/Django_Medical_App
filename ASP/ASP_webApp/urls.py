from django.urls import path

from . import views

app_name = 'ASP_webApp'

urlpatterns = [

    # --------------------------Register-----------------------------------
    path('createToken/', views.createTokenpage.as_view()),
    path('createAccount', views.createAccount.as_view()),
    path('tokenValidate', views.tokenValidate.as_view()),
    path('register/', views.registerPage.as_view()),

    # --------------------------Login/Logout-------------------------------
    path('menu/', views.menu.as_view()),
    path('login/', views.UserLogin.as_view()),
    path('login/validate', views.validate.as_view()),
    path('logout/', views.Logout.as_view()),

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
    path('D/main/dispatchDetailJson/', views.DispatchPage.dispatchViewDetailJson, name='dispatchPageDetailJson'),
    path('D/main/getItinerary/', views.DispatchPage.getItinerary, name='getItinerary'),
    path('D/main/dispatchUpdate/', views.DispatchPage.dispatchUpdate, name='dispatchUpdate'),
    # --------------------------Warehouse Personnel------------------------
    path('WHP/main/', views.warehousePage.warehouseView, name='whpPage'),
    path('WHP/main/processOrder/', views.warehousePage.orderProcess, name='whpProcessOrder'),
    path('WHP/main/PDF/', views.warehousePage.getShippingLabel, name='whpPDF'),
    path('WHP/main/updateStatus/', views.warehousePage.updateStatus, name='whpPDF'),
]