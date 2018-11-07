"""ASP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

import system.urls as system_app

# 定義了網站url到view的映射。雖然這裡可以包含所有的url，但是更常見的做法是把應用相關的url包含在相關應用中，你可以在接下來的教程裡看到。

urlpatterns = [
    # path('asp/', include('system.urls')),
    path('admin/', admin.site.urls),
    # path('register/',),
    path('CM/createOrderPage/', include("createOrderPage.urls")),
    path('CM/view_detail/<int:pk>/', system_app.views.DetailView.as_view(), name='detail'),
    path('D/view', system_app.views.DispatchView.as_view(), name='dispatch'),
    path(r'displayByCategory<slug:cat>/', system_app.views.displayByCategory, name='displayByCategory'),
    path('CM/order/<int:orderID>/', system_app.views.orderView, name='order'),
    path('dispatcher/dispatchUpdate/', system_app.views.DispatchView.as_view(), name='dispatch_update'),
]
