# Create your views here.

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.utils import timezone
from .models import Include, Order, Supply
import json


# --------------------------ASP_webApp------------------------------
# ---------------------------------------------------------------------
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
            # this line is obviously wrong
            itemsinfo = json.loads(items)
            for item in itemsinfo:
                orderInclude = Include.create(resultOrder.pk, item['item_id'], item['quantity'])
                orderInclude.save()
            result = "success"
        else:
            result = None
        return render(request, "CM/createOrderPage.html", {"result": result})

class DetailView(generic.DetailView):
    model = Supply  # where to search for primary key
    template_name = "CM/detail.html"


# detail of specific order
# preforming query for cretaing objects.
def orderView(request, orderID):
    order = Order.objects.get(pk=orderID)
    supply = Include.objects.filter(order_id=orderID)
    list = {'order': order, 'supplyList': supply}
    return render(request, "CM/order.html", list)


# -----------------------------Dispatcher------------------------------
# ---------------------------------------------------------------------

# for generic lsit view
# use def get_queryset and return a list
class DispatchView(generic.ListView):
    context_object_name = 'orderList'
    # equal to pass a list
    # {orderList: queryset}
    template_name = "Dispatcher/dispatch.html"

    def get_queryset(self):
        return Order.objects.filter(status="Queued for dispatch").order_by('priority')


class DispatchUpdate(generic.ListView):
    context_object_name = 'orderList'
    template_name = "Dispatcher/dispatch.html"

    # update status and dispatch datetime of all selected orders
    def dispatchUpdate(self):
        orderList = Order.objects.filter(status="Queued for dispatch").order_by('priority')
        orderList.objects.update(status="Dispatched")
        dateTime = timezone.now()
        orderList.objects.update(dispatchedDatetime=dateTime)
        orderList.save()


# def createItinerary(self):
    # create itinerary file

# if not use generic view, use render to call html
# cat is the category name
def displayByCategory(request, cat):
    supply = Supply.objects.filter(category=cat)
    list = {'supply': supply}
    return list

# ---------------------------WarehousePersonnel------------------------
# ---------------------------------------------------------------------