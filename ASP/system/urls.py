from django.urls import path

from . import views

app_name = "system"
urlpatterns = [
    path('', views.index, name='index'),
	#to use generic view, only primary key can be included in the url
	path('<int:pk>/detail/', views.DetailView.as_view(), name='detail'),
	path('dispatch',views.DispatchView.as_view(),name ='dispatch'),
	path('<str:cat>',views.displayByCategory,name='displayByCategory'),
	path('<int:orderID>/order',views.orderView,name='order'),
]