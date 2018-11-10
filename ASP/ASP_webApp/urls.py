from django.urls import path

from . import views

urlpatterns = [
    # --------------------------Register-----------------------------------
    # path('register/',),

    # --------------------------ASP_webApp------------------------------
    path('CM/main/', views.createOrderPage.as_view()),
    path('CM/createOrder/', views.createOrderPage.as_view(), name='order'),
    path('CM/view_detail/<int:pk>/', views.DetailView.as_view(), name='detail'),

    # --------------------------Dispatcher---------------------------------
    path('D/main', views.DispatchView.as_view(), name='dispatch'),
    path('D/dispatchUpdate/', views.DispatchUpdate.as_view(), name='dispatch_update'),

    # --------------------------Warehouse Personnel------------------------
    path('WHP/displayByCategory<slug:cat>/', views.displayByCategory, name='displayByCategory'),
]