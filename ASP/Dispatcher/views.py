"""
This is where the urls.py will redirect to.
it redirects to one of the functions below.
Noted that an "request" argument must be presented as the first argument, to handle HTTP stuff (I guess),
except for Generic view (which I have no idea on)
"""
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Supply, Order, Include
import json

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