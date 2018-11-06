from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Supply,Order,Include

#temp index page
def index(request):
	return HttpResponse("index page")

#for generic detail view	
#use the primary key in the url
#detail of a supply
class DetailView(generic.DetailView):
	model = Supply#where to search for primary key
	template_name = "system/detail.html"
	
#for generic lsit view
#use def get_queryset and return a list
class DispatchView(generic.ListView):
	context_object_name = 'orderList'
	#equal to pass a list
	#{orderList: queryset}
	template_name = "system/dispatch.html"
	def get_queryset(self):
		return Order.objects.filter(status="Queued for dispatch").order_by('orderedDatetime')
		
#if not use generic view, use render to call html
#cat is the category name
def displayByCategory(request,cat):
	supply = Supply.objects.filter(category=cat)
	list = {'list':supply}
	return render(request,"system/displayByCategory.html",list)
	
#detail of specific order
def orderView(request,orderID):
	order = Order.objects.get(pk=orderID)
	supply = Include.objects.filter(order_id=orderID)
	list = {'order':order,'supplyList':supply}
	return render(request,"system/order.html",list)

def createOrder(request):
	return render(request, "system/createOrder.html")