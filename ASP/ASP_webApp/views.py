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


class CreateOrderPage(View):
    def createOrderView(request):
        categories = Supply.objects.all().values('category').distinct()
        return render(request, "CM/createOrderPage.html", context={'categories': categories})

    def createOrder(request):
        # user wants to create an order
        query = request.POST.get('order')
        # need a verification block here
        try:
            orderObject = json.loads(query)
        except json.JSONDecodeError as e:
            return HttpResponse("Fail")
        clinic_id = orderObject['clinic_id']
        account_id = orderObject['account_id']
        dateTime = timezone.now()
        priority = orderObject['priority']
        weight = orderObject['weight']
        order = Order.create(priority=priority, ODatetime=dateTime, clinic=clinic_id, weight=weight, account=account_id)
        itemsinfo = orderObject['cart']
        order.save()
        # before submitting order to the database we has to check if the required quantity is correct or not
        # we need to get item id...
        for item in itemsinfo:
            orderInclude = Include(order=order, supply=Supply.objects.get(id=item['item_id']), quantity=item['quantity'])
            orderInclude.save()
        return HttpResponse("Success")

    # if not use generic view, use render to call html
    # cat is the category name
    def displayByCategory(request):
        # data = json.load(request.POST)
        # get the category of the returned JSON object
        cat = request.POST.get("category", "")
        # returned value
        results = Supply.objects.filter(category=cat).values('id', 'name', 'weight', 'description')
        json_result = []
        for result in results:
            json_result.append(result)
        return render_to_response("CM/category_load.html", {'results': json_result})

    def displayByCategoryJson(request):
        # data = json.load(request.POST)
        # get the category of the returned JSON object
        cat = request.POST.get("category", "")
        # returned value
        results = Supply.objects.filter(category=cat).values('id', 'name', 'weight', 'description')
        json_result = []
        for result in results:
            json_result.append(result)
        return JsonResponse(json_result, safe=False)

    def viewOrder(request):
        account_id = request.POST.get("account_id", "")

        # first get their order ID (distinct), get their supply_id and quantity,
        # then merge them together, and get their priority and weight later.
        order_ids = []
        for id_result in Order.objects.all().filter(ordering_account=account_id).values("id").order_by("-id"):
            order_ids.append(id_result['id'])
        # print(order_ids)

        json_result = []
        for order_id in order_ids:
            temp_dict = {}
            temp_dict["order_id"] = order_id
            temp_dict["priority"] = Order.objects.get(id=order_id).priority
            temp_dict["items"] = []
            temp_dict["status"] = Order.objects.get(id=order_id).status
            for order_object in Include.objects.all().filter(order=order_id).values():
                temp_dict["items"].append({ "name": Supply.objects.get(id=order_object["supply_id"]).name, "supply_id": order_object["supply_id"], "quantity": order_object["quantity"]})
            temp_dict["total_weight"] = Order.objects.get(id=order_id).weight
            json_result.append(temp_dict)
        return render_to_response("CM/viewOrder.html", {'results': json_result})

    def orderAction(request):
        order_id = request.POST.get("orderID", "")
        if (Order.objects.get(id=order_id).status != "Queued for Processing"):
            Order.objects.filter(id=order_id).update(status="Delivered")
        else:
            Order.objects.filter(id=order_id).update(status="Cancelled")
        return HttpResponse("Success")

# -----------------------------Dispatcher------------------------------
# ---------------------------------------------------------------------

# use return a json containing all the orders that are "Queued for Dispatch"
class DispatchPage(View):

    def dispatchView(request):
        result = Order.objects.filter(status="Queued for Dispatch")\
                                        .values('id', 'name', 'priority', 'ordering_clinic', 'weight')\
                                        .order_by('priority', 'orderedDatetime', 'id')
        json_result = []
        max_weight = 25.0
        for item in result:
            max_weight -= item.weight
            if max_weight < 0:
                break
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
        # initial loading.
        return render_to_response("Dispatcher/dispatch.html", {'results': json_result})
    
    
    
    # update status and dispatch datetime of all selected orders
    def dispatchUpdate(request):
        orders = request.POST.get("orderSet")
        for order_id in orders:
            singleOrder = Order.objects.filter(id=order_id).update(status="Dispatched")
            dateTime = timezone.now()
            singleOrder.objects.update(dispatchedDatetime=dateTime)
            singleOrder.save()
        # should be success message, don't need to render.
        return render(request, "Dispatcher/dispatch.html", {'message' : 'success'})
    
    # create itinerary file
    # orders should be a list of order ids
    def createItinerary(request):
        orders = request.POST.get("orderSet")
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
                destination = Order.objects.get(id=order_id).location
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
class warehousePage(View):
    # view priority queue
    def warehouseView(request):
        orderList = Order.objects.filter(status="Queued for Processing").order_by('priority', 'orderedDatetime', 'id')
        return render(request, "Dispatcher/dispatch.html", {'results': orderList})


    # remove order from the top to pick and pack (change status to "processing by warehouse")
    # and return the details of the selected order
    def orderSelect(request):
        chosen = Order.objects.filter(status="Queued for Processing").order_by('priority', 'orderedDatetime', 'id')[:1]
        chosen.objects.update(status="Processing by Warehouse")
        chosen.save()
        jsonresult = []
        jsonresult.append(chosen)
        return render(request, "WHP/warehouse.html", {'results': jsonresult})


       # get a shipping label consists of (order_id, supplies name, quantity, priority, destination name)
       # and update status of the selcted order (status ==> "Queued for Dispatch")
    def getShippingLabel(request, order_id):
        order_selected = Order.objects.filter(id=order_id)
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