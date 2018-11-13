from django.urls import path

from . import views

app_name = 'ASP_webApp'

urlpatterns = [
    # --------------------------Register-----------------------------------
    # path('register/',),

    # --------------------------Clinic Manager-----------------------------
    path('CM/main/', views.createOrderPage.as_view()),
    path('CM/createOrder/', views.createOrderPage.as_view(), name='order'),
    path('CM/displayByCategory/', views.createOrderPage.displayByCategory, name='displayByCategory'),

    path('CM/view_detail/<int:pk>/', views.DetailView.as_view(), name='detail'),

    # --------------------------Dispatcher---------------------------------
    path('D/main', views.DispatchView.as_view(), name='dispatch'),
    path('D/dispatchUpdate/', views.DispatchUpdate.as_view(), name='dispatch_update'),

    # --------------------------Warehouse Personnel------------------------

]
