# Create your views here.

from django.shortcuts import *
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.utils import timezone
from .models import *
import csv
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
        query = request.POST.get('order', "")
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
            orderInclude = Include(order=order, supply=Supply.objects.get(id=item['item_id']),
                                   quantity=item['quantity'])
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
                temp_dict["items"].append({"name": Supply.objects.get(id=order_object["supply_id"]).name,
                                           "supply_id": order_object["supply_id"],
                                           "quantity": order_object["quantity"]})
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

class DispatchPage(View):
    # use return a json containing all the orders that are "Queued for Dispatch"

    def dispatchView(request):
        return render_to_response("Dispatcher/dispatchPage.html")

    def dispatchViewDetail(request):
        # get all order id with "Queued for Dispatch" status, render into the tempalte.
        result = []
        results = Order.objects.all().filter(status="Queued for Dispatch"). \
            values('id', 'priority', 'weight', 'processedDatetime', 'ordering_clinic') \
            .order_by('priority', 'processedDatetime', 'id')
        for ele in results:
            result.append(ele)
        json_result = []
        max_weight = 25.0
        for item in result:
            max_weight -= item['weight']
            if max_weight < 0:
                break
            single_order = {}
            single_order["order_id"] = item['id']
            single_order["priority"] = item['priority']
            single_order["processedDatetime"] = item['processedDatetime']
            single_order["clinic"] = item['ordering_clinic']
            single_order["weight"] = item['weight']
            order_items = Include.objects.filter(order_id=item['id']).values('supply_id', 'quantity')
            # get all supplies of the corresponding order
            items = []
            for info in order_items:
                supply_item_id = Supply.objects.get(
                    id=info["supply_id"]).id  # should be index of image, it's for frontend image.
                supply_item_name = Supply.objects.get(id=info["supply_id"]).name
                items.append({"id": supply_item_id, "name": supply_item_name, "quantity": info['quantity']})
            single_order["items"] = items
            json_result.append(single_order)
        return render_to_response("Dispatcher/dispatchDetail.html", {'results': json_result})

    def dispatchViewDetailJson(request):
        # return item JSON information to the website.
        result = []
        results = Order.objects.all().filter(status="Queued for Dispatch"). \
            values('id', 'priority', 'weight', 'processedDatetime', 'ordering_clinic') \
            .order_by('priority', 'processedDatetime', 'id')
        for ele in results:
            result.append(ele)
        json_result = []
        max_weight = 25.0
        for item in result:
            max_weight -= item['weight']
            if max_weight < 0:
                break
            json_result.append(item['id'])
        return JsonResponse(json_result, safe=False)

    # create itinerary file
    # orders should be a list of order ids
    def getItinerary(request):
        result = []
        results = Order.objects.all().filter(status="Queued for Dispatch"). \
            values('id', 'priority', 'weight', 'processedDatetime', 'ordering_clinic') \
            .order_by('priority', 'processedDatetime', 'id')
        for ele in results:
            result.append(ele)
        orders = []
        max_weight = 25.0
        for item in result:
            max_weight -= item['weight']
            if max_weight < 0:
                break
            orders.append(item['id'])
        # sets the hospital's id as first location
        hospital_location = Location.objects.get(name="Queen Mary Hospital Drone Port")
        location_id = hospital_location.pk
        order_ids = orders.copy()
        # items = []
        # check sequence for locations
        #buffer = io.StringIO()
        with open('itinerary.csv', 'w') as buffer:
            spamwriter = csv.writer(buffer, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            while order_ids:
                minimum = 999999
                temp = None
                for order_id in order_ids:
                    destination = Order.objects.get(id=order_id).ordering_clinic_id
                    if destination >= location_id:
                        d = Distance.objects.get(distanceFrom=location_id, distanceTo=destination).distance
                    else:
                        d = Distance.objects.get(distanceFrom=destination, distanceTo=location_id).distance
                    if d < minimum:
                        temp = destination
                        minimum = d
                location_id = temp
                order_id2 = order_ids.copy()
                for order_id in order_ids:
                    order_location = Order.objects.get(id=order_id).ordering_clinic_id
                    if order_location == location_id:
                        order_id2.remove(order_id)
                order_ids = order_id2
                cur_location = Location.objects.get(id=temp)
                # items.append([cur_location.name, cur_location.latitude, cur_location.longitude, cur_location.altitude])
                spamwriter.writerow([cur_location.name, cur_location.latitude, cur_location.longitude, cur_location.altitude])
            # items.append(['Queen Mary Hospital Drone Port', hospital_location.latitude, hospital_location.longitude,
            #             hospital_location.altitude])
            spamwriter.writerow(['Queen Mary Hospital Drone Port', hospital_location.latitude, hospital_location.longitude,
                        hospital_location.altitude])
        with open('itinerary.csv', 'r') as buffer:
            response = HttpResponse(buffer, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=itinerary.csv'
            return response

    # update status and dispatch datetime of all selected orders
    def dispatchUpdate(request):
        orders = request.POST.getlist("item")
        for order_id in orders:
            Order.objects.filter(id=int(order_id)).update(status="Dispatched", dispatchedDatetime=timezone.now())
        return HttpResponse("Success")


# ---------------------------WarehousePersonnel------------------------
# ---------------------------------------------------------------------
class warehousePage(View):
    # view priority queue
    def warehouseView(request):
        orderList = Order.objects.filter(status="Queued for Processing").order_by('priority', 'orderedDatetime', 'id').values("ordering_clinic_id", "orderedDatetime")
        for order in orderList:
            order["ordering_clinic"] = Location.objects.get(id=order.pop("ordering_clinic_id", None)).name
        print(orderList)
        return render(request, "WHP/warehouseManage.html", {'results': orderList})

    # remove order from the top to pick and pack (change status to "processing by warehouse")
    # and return the details of the selected order
    def orderProcess(request):
        order_obj = Order.objects.filter(status="Queued for Processing").order_by('priority', 'orderedDatetime', 'id')[:1]
        # chosen.update(status="Processing by Warehouse")
        print(order_obj)
        jsonresult = []
        for obj in order_obj:
            jsonresult.append(obj)
        print(jsonresult)
        return render(request, "WHP/warehouseManage.html", {'process_results': jsonresult})

    # get a shipping label consists of (order_id, supplies name, quantity, priority, destination name)
    # and update status of the selcted order (status ==> "Queued for Dispatch")
    def getShippingLabel(request):
        order_id = request.POST.get("order_id", "")

        order_selected = Order.objects.get(id=order_id)
        items = Include.objects.get(order=order_id)
        quantity = 0
        for item in items:
            quantity += item.quantity
        order_account = Account.objects.get(id=order_selected.ordering_account)
        account_name = order_account.firstname + " " + order_account.lastname
        location_name = Location.objects.get(id=order_selected.ordering_clinic).name
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setLineWidth(.3)
        pdf.setFont('Helvetica', 12)

        pdf.drawString(30, 750, 'Queen Mary ')
        pdf.drawString(30, 735, 'Hospital Drone Port')
        pdf.drawString(450, 750, 'ORDER ID:')
        pdf.drawString(500, 750, order_id)

        pdf.line(480, 747, 580, 747)

        pdf.drawString(275, 725, 'QUANTITY:')
        pdf.drawString(500, 725, quantity)
        pdf.line(378, 723, 580, 723)

        pdf.drawString(30, 703, 'RECEIVED BY:')
        pdf.line(120, 700, 600, 700)
        pdf.drawString(120, 703, account_name)
        pdf.drawString(450, 703, 'PRIORITY:')
        pdf.drawString(500, 703, order_selected.priority)
        pdf.drawString(30, 665, 'DESTINATION: ')
        pdf.line(120, 660, 600, 660)
        pdf.drawString(30, 665, location_name)
        pdf.showPage()
        pdf.save()
        return FileResponse(buffer, as_attachment=True, filename='shipping_label.pdf')

    def updateStatus(request):
        order_id = request.POST.get("order_id", "")
        order_selected = Order.objects.filter(id=order_id)
        order_selected.objects.update(status="Queued for Dispatch")
        dateTime = timezone.now()
        order_selected.objects.update(processedDatetime=dateTime)
        order_selected.save()
        return HttpResponse("Success")
