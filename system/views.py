from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Supply,Order,Include

# Create your views here.
def index(request):
	return HttpResponse("index page")
	
class DetailView(generic.DetailView):
	model = Supply
	template_name = "system/detail.html"
	
class DispatchView(generic.ListView):
	context_object_name = 'orderList'
	template_name = "system/dispatch.html"
	def get_queryset(self):
		return Order.objects.filter(status="Queued for dispatch").order_by('orderedDatetime')
		
def displayByCategory(request,cat):
	supply = Supply.objects.filter(category=cat)
	list = {'list':supply}
	return render(request,"system/displayByCategory.html",list)
	
def orderView(request,orderID):
	order = Order.objects.get(pk=orderID)
	supply = Include.objects.filter(order_id=orderID)
	list = {'order':order,'supplyList':supply}
	return render(request,"system/order.html",list)
	