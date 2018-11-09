# Create your views here.

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import *
from django.utils import timezone
from .models import Include, Order, Supply
import json

class createOrderPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, "CM/createOrderPage.html")

    def post(self, request, *args, **kwargs):
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
        return render(request, "CM/createOrderPage.html", {"result": result})

class DetailView(DetailView):
    model = Supply  # where to search for primary key
    template_name = "D/../ClinicManager/templates/CM/detail.html"


# detail of specific order
# preforming query for cretaing objects.
def orderView(request, orderID):
    order = Order.objects.get(pk=orderID)
    supply = Include.objects.filter(order_id=orderID)
    list = {'order': order, 'supplyList': supply}
    return render(request, "CM/order.html", list)