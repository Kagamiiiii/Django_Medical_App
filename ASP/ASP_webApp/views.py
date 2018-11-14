# Create your views here.

from django.shortcuts import *
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.utils import timezone
from .models import *
import json
import io
from reportlab.pdfgen import canvas

# --------------------------Clinic Manager-----------------------------
# ---------------------------------------------------------------------

"""
CREATE ORDER LOGIC / REQUIRED DATA

return data:
{
    "priority" : 'high'
    "clinic_id" : <int>
    "account_id" : <int>
    "weight" : <int>
    "items" : [{
             "id": (some supply_id, extracted with Supply.pk),
             "quantity": <int>
          },
          {
             "id": (some supply_id, extracted with Supply.pk),
             "quantity": <int>
          },
          ...
        ]
    }
}

#noted that all return message and id should be extracted from backend with Django HTML 
to ensure it's all correct.

1. Get request from frontend. 
    Frontend must be generated by Django HTML 
    in order to prerecord it's Supply.pk (supply id)

... after creating order and submitting ...

2. obtain the json object; parse it.
3. get clinic id, that's for the "orderInfo" thing.
4. location should be known, can check through db query with clinic_id
5. for each item in the list:
    include order_id, supply_id, quantity;
    save them.
6. return success information.

"""


class createOrderPage(View):
    def get(self, request, *args, **kwargs):
        categories = Supply.objects.all().values('category').distinct()
        return render(request, "CM/createOrderPage.html", context={'categories': categories})

    def post(self, request, *args, **kwargs):
        # user wants to create an order
        query = request.POST.get('order')
        # need a verification block here
        try:
            orderObject = json.loads(query)
        except json.JSONDecodeError as e:
            return render(request, template_name="CM/createOrderPage.html", context={"result": "fail"})
        clinic_id = orderObject['clinic_id']
        account_id = orderObject['account_id']
        dateTime = timezone.now()
        priority = orderObject['priority']
        weight = orderObject['weight']
        Order.objects.create(priority=priority, ODatetime=dateTime, weight=weight)
        itemsinfo = orderObject['items']
        # before submitting order to the database we has to check if the required quantity is correct or not
        # we need to get item id...
        for item in itemsinfo:
            orderInclude = Include(order=Order.pk, supply=item['item_id'], quantity=item['quantity'])
            orderInclude.save()
        OrderInfo.objects.create(order=Order.pk, location=Location.objects.get(clinic_id=clinic_id), account=account_id)
        return render(request, template_name="CM/createOrderPage.html", context={"result": "success"})

    # if not use generic view, use render to call html
    # cat is the category name
    def displayByCategory(request):
        if request.method != 'POST':
            return render_to_response()
        # data = json.load(request.POST)
        # get the category of the returned JSON object
        cat = request.POST.get("category", "")
        # returned value
        results = Supply.objects.filter(category=cat).values('id', 'name')
        json_result = []
        for result in results:
            json_result.append(result)
        return render_to_response("CM/category_load.html", {'results': json_result})


# View addition information of that item.
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

# use return a json containing all the orders that are "Queued for Dispatch"
def dispatchView(request):

    result = Order.objects.filter(status="Queued for Dispatch")\
                                    .values('id', 'name', 'priority', 'ordering_clinic', 'weight')\
                                    .order_by('priority')
    json_result = []
    for item in result:
        single_order = {}
        single_order["order_id"] = item.id
        single_order["order_name"] = item.name
        single_order["priority"] = item.priority
        single_order["clinic"] = item.ordering_clinic
        single_order["weight"] = item.weight
        order_items = Include.objects.filter(order=item.id).values('supply', 'quantity')
        # get all supplies of the corresponding order
        children = []
        for info in order_items:
            item_name = Supply.objects.get(id=info.supply).values('name')
            children.append({"name" : item_name, "quantity" : info.quantity})
        single_order["children"] = children
        json_result.append(single_order)

    return render_to_response("Dispatcher/dispatch.html", {'results': json_result})



# update status and dispatch datetime of all selected orders
def dispatchUpdate(request, self):
    orderList = Order.objects.filter(status="Queued for Dispatch").order_by('priority')
    orderList.objects.update(status="Dispatched")
    dateTime = timezone.now()
    orderList.objects.update(dispatchedDatetime=dateTime)
    orderList.save()
    return render(request, "Dispatcher/dispatch.html", {'message' : 'success'})

# def createItinerary(self):
# create itinerary file
# orders should be a list of order idss
def createItinerary(request, orders):
   hospitalName = 'Queen Mary Hospital Drone Port'
   # sets the hospital's id as first location
   hospital_location = Location.objects.get(name=hospitalName)
   location_id = hospital_location.pk
   order_ids = orders.copy()
   items = []
   # check sequence for locations
   while order_ids:
       min = 999999
       temp = None
       for order_id in order_ids:
           destination = OrderInfo.objects.get(order=order_id).location
           d = Distance.objects.get(distanceFrom=location_id, distanceTo=destination).distance
           if d < min:
               temp = order_id
               min = d
       location_id = temp
       order_ids.remove(temp)
       cur_location = Location.objects.get(id=temp)
       item = { 'name' : cur_location.name,
                'latitude' : cur_location.latitude,
                'longitude' : cur_location.longitude,
                'altitude' : cur_location.altitude }
       items.append(item)
   item = { 'name' : 'Queen Mary Hospital Drone Port',
            'latitude' : hospital_location.latitude,
            'longitude' : hospital_location.longitude,
            'altitude' : hospital_location.altitude }
   items.append(item)
   return render(request, "Dispatcher/dispatch.html", {'results': items})

# ---------------------------WarehousePersonnel------------------------
# ---------------------------------------------------------------------
class WarehouseView(generic.ListView):
    context_object_name = 'warehouseList'
    # equal to pass a list
    # {orderList: queryset}
    template_name = "WHP/warehouse.html"

    # view priority queue
    def get_queryset(self):
        return Order.objects.filter(status="Queued for Processing").order_by('priority')


    # remove order from the top to pick and pack (change status to "processing by warehouse")
    # and return the details of the selected order
def orderSelect(request):
    chosen = Order.objects.filter(status="Queued for Processing").order_by('priority')[:1]
    chosen.objects.update(status="Processing by Warehouse")
    chosen.save()
    jsonresult = []
    jsonresult.append(chosen)
    return render(request, "WHP/warehouse.html", {'results': jsonresult})


    # get a shipping label consists of (order_id, supplies name, quantity, priority, destination name)
    # and update status of the selcted order (status ==> "Queued for Dispatch")
def getShippingLabel(request, order_id):
    order_selected = Order.objects.get(id=order_id)
    items = Include.objects.filter(order=order_id)
    quantity = 0
    for item in items:
        quantity += item.quantity
    buffer =  io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setLineWidth(.3)
    pdf.setFont('Helvetica', 12)

    pdf.drawString(30, 750, 'Queen Mary ')
    pdf.drawString(30, 735, 'Hospital Drone Port')
    pdf.drawString(450, 750, 'Order id:')
    pdf.drawString(500, 750, order_id)

    pdf.line(480, 747, 580, 747)

    pdf.drawString(275, 725, 'Quantity:')
    pdf.drawString(500, 725, quantity)
    pdf.line(378, 723, 580, 723)

    pdf.drawString(30, 703, 'RECEIVED BY:')
    pdf.line(120, 700, 580, 700)
    pdf.drawString(120, 703, order_selected.name)
    pdf.drawString(450, 703, 'Priority:')
    pdf.drawString(500, 703, order_selected.priority)
    pdf.showPage()
    pdf.save()
    order_selected.objects.update(status="Queued for Dispatch")
    order_selected.save()
    return FileResponse(buffer, as_attachment=True, filename='shipping_label.pdf')