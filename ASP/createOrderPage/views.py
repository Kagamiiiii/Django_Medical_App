from django.shortcuts import render


# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Order, Include
import json

def createOrderPage(request):
    return render(request, "system/CM/createOrder.html")

def createOrder(request):
    query = request.POST.get('order')
    if query:
        obj = json.loads(query)
        clinic = obj['clinic']
        dateTime = timezone.now()
        priority = obj['priority']
        items = obj['cart']
        # weight = obj['weight']
        resultOrder = Order.create(priority=priority, ODatetime=dateTime, cid=clinic)  # weight=weight)
        resultOrder.save()
        itemsinfo = json.loads(items)
        for item in itemsinfo:
            orderInclude = Include.create(resultOrder.pk, item['item_id'], item['quantity'])
            orderInclude.save()
        result = "success"
    else:
        result = None
    return render(request, "system/CM/createOrderPage.html", {"result": result, })