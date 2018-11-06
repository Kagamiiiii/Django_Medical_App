"""
From browser request, the outer system (ASP) maps the requested URL according to the redirection logic of urls.py,
into individual APPS (a website could contain multiple applications).
In this case ASP(outer system) redirects url requests into the urls.py file in this directory (system directory).
it pattern matches (using regex) the first argument of items in the list urlpatterns.
If there's a match matched, it's going to jump to the function that handles the request in views.py file.
"""
from django.urls import path

from . import views

app_name = "system"

urlpatterns = [
    # path('', views.index, name='index'),
    # to use generic view, only primary key can be included in the url
    path('detail/<int:pk>/', views.DetailView.as_view(), name='detail'),
    # noted there maybe some requests with parameters in the link,
    # for example 4/detail. In this case, the <int:pk> clause matches the integer
    # and passes that as an argument to the function DetailView in views.py so they can handle them.
    # the name option, however, is the assign a name for such redirection, so in other files you can
    # use that abbreviation to represent this.
    path('dispatch/', views.DispatchView.as_view(), name='dispatch'),
    path('<str:cat>', views.displayByCategory, name='displayByCategory'),
    path('order/<int:orderID>/', views.orderView, name='order'),
    path('clinic_manager/create_order/', views.createOrder2, name='create_order'),
    path('dispatcher/dispatchUpdate/', views.DispatchView.dispatchUpdate(), name='dispatch_update'),
]
