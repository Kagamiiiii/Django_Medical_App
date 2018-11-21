# Create your views here.

from django.shortcuts import *
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic, View
from django.utils import timezone
from .models import *
from reportlab.pdfgen import canvas
from django.contrib.auth import *
from django.shortcuts import redirect
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
import csv
import json
import io


# ---------------------------Token creation----------------------------
# ---------------------------------------------------------------------

class createTokenpage(View):
    def get(self, request, *args, **kwargs):
        return render(request, "M/create token.html")


# ----------------------------Registration-----------------------------
# ---------------------------------------------------------------------

class registerPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, "M/registration page.html")


class tokenValidate(View):
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        if token == '-':
            return HttpResponse("No such token")
        try:
            account = Account.objects.get(token=token)
        except:
            return HttpResponse("No such token")

        if account is None:
            return HttpResponse("No such token")

        return HttpResponse(
            json.dumps({'email': account.email, 'location': account.worklocation.name, 'role': account.role}),
            content_type="application/json")


class createAccount(View):
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')

        try:
            User.objects.get(username=request.POST.get('username'))
            return HttpResponse("Username is in use.")
        except:
            pass

        account = Account.objects.get(token=token)

        if account.username != '':
            return HttpResponse('Token has been redeemed')

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.create_user(username, email, password)
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')
        user.save()
        account.username = request.POST.get('username')
        account.email = request.POST.get('email')
        account.password = request.POST.get('password')
        account.firstname = request.POST.get('firstname')
        account.lastname = request.POST.get('lastname')
        # User created

        account.token = '-'
        account.save()
        # account edited

        # add user to group
        group = Group.objects.get(name=account.role)
        user.groups.add(group)

        return HttpResponse('')


# ------------------------------Login----------------------------------
# ---------------------------------------------------------------------

class UserLogin(View):
    def get(self, request, *args, **kwargs):
        return render(request, "M/login.html")


class menu(View):
    def get(self, request, *args, **kwargs):

        try:
            inputusername = request.session['username']
            inputpassword = request.session['password']
        except:
            return redirect("/login/")

        """
        try:
            request.session['role']
        except:
            return redirect("/login/")
        if request.session['role'] != 'Clinic Manager':  # 'Warehouse Personnel' 'Dispatcher'
            return redirect("/login/")
        """

        user = User.objects.get(username=request.session['username'])

        # request.session['role'] = user.groups.all()[0].name

        if user is None:
            return redirect('/login/')
        user_account = Account.objects.filter(username=inputusername, password=inputpassword).values('id', 'role')

        for user_ac in user_account:
            request.session['id'] = user_ac['id']
            if user_ac['role'] == "Clinic Manager":
                return redirect("/CM/main/")
            if user_ac['role'] == 'Dispatcher':
                return redirect("/D/main")
            if user_ac['role'] == 'Warehouse Personnel':
                return redirect("/WHP/main")


class validate(View):
    def post(self, request, *args, **kwargs):
        form = request.POST

        if form is not None:
            username = form['username']
            password = form['password']

            user = authenticate(username=username, password=password)

            if user is None:
                return redirect("/login/")
            if user.is_active:
                login(request, user)
                request.session['username'] = username
                request.session['password'] = password
                return redirect("/menu/")


class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("/login/")


# --------------------------Clinic Manager-----------------------------
# ---------------------------------------------------------------------


class CreateOrderPage(View):
    def createOrderView(request):
        categories = Supply.objects.all().values('category').distinct()
        return render(request, "CM/createOrderPage.html", context={'categories': categories})

    def createOrder(request):
        account_id = request.session['id']
        # user wants to create an order
        query = request.POST.get('order', "")
        # need a verification block here
        try:
            orderObject = json.loads(query)
        except json.JSONDecodeError as e:
            return HttpResponse("Fail")
        clinic_id = None
        print(account_id)
        workingclinic = Account.objects.filter(id=account_id).values('worklocation')
        print(workingclinic)
        for x in workingclinic:
            clinic_id = x['worklocation']
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
        return redirect("/CM/main/")

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
        #account_id = request.POST.get("account_id", "")
        account_id = request.session['id']
        print(account_id)
        # first get their order ID (distinct), get their supply_id and quantity,
        # then merge them together, and get their priority and weight later.
        order_ids = []
        for id_result in Order.objects.all().filter(ordering_account=int(account_id)).values("id").order_by("-id"):
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
        with open('itinerary.csv', 'w') as buffer:
            spamwriter = csv.writer(buffer, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['Location name', 'Latitude', 'Longitude', 'Altitude'])
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
        return redirect("/D/main")


# ---------------------------WarehousePersonnel------------------------
# ---------------------------------------------------------------------
class warehousePage(View):
    # view priority queue
    def warehouseView(request):
        orderList = Order.objects.filter(status="Queued for Processing").order_by('priority', 'orderedDatetime', 'id').values("ordering_clinic_id", "orderedDatetime")
        for order in orderList:
            order["ordering_clinic"] = Location.objects.get(id=order.pop("ordering_clinic_id", None)).name
        return render(request, "WHP/warehouseManage.html", {'results': orderList})

    # remove order from the top to pick and pack (change status to "processing by warehouse")
    # and return the details of the selected order
    def orderProcess(request):
        order_objects = Order.objects.filter(status="Queued for Processing").values('id', 'weight', 'priority', 'orderedDatetime', 'ordering_clinic')\
                                        .order_by('priority', 'orderedDatetime', 'id', 'weight')[:1]
        order_id = None
        order_json = {}
        for order_obj in order_objects:
            order_id = int(order_obj['id'])
            order_items = Include.objects.filter(order=order_id).values('quantity', 'order', 'supply')
            clinicID= order_obj['ordering_clinic']
            order_json["id"] = order_obj['id']
            order_json["clinic"] = Location.objects.get(id=clinicID).name
            order_json["priority"] = order_obj['priority']
            order_json["weight"] = order_obj['weight']
            order_json["orderedDatetime"] = order_obj['orderedDatetime']
            children = []
            for item in order_items:
                item_detail = Supply.objects.get(id=item['supply'])
                item_json = {}
                item_json['supply_id'] = item_detail.id
                item_json['name'] = item_detail.name
                item_json['quantity'] = item['quantity']
                children.append(item_json)
            order_json["items"] = children
        ordered = Order.objects.filter(id=order_id)
        ordered.update(status="Processing by Warehouse")
        return render(request, "WHP/warehouseDetail.html", {'process_results': order_json})

    # get a shipping label consists of (order_id, supplies name, quantity, priority, destination name)
    # and update status of the selected order (status ==> "Queued for Dispatch")
    def getShippingLabel(request):
        order_result = Order.objects.filter(status="Processing by Warehouse").values('ordering_account', 'id', 'ordering_clinic', 'priority')
        if not order_result:
            return render(request, "WHP/warehouseDetail.html", {'message': "error"})
        for order_selected in order_result:
            order_id = order_selected['id']
            items = Include.objects.filter(order=order_id).values('quantity')
            quantity = 0
            for item in items:
                quantity += item['quantity']
            account_name = order_selected['ordering_account']
            order_account = Account.objects.get(id=account_name)
            account_name = order_account.firstname + " " + order_account.lastname
            order_clinic = order_selected['ordering_clinic']
            location_name = Location.objects.get(id=order_clinic).name
            priority = order_selected['priority']
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer)
            pdf.setLineWidth(.3)
            pdf.setFont('Helvetica', 16)

            pdf.drawString(30, 800, 'Queen Mary ')
            pdf.drawString(30, 775, 'Hospital Drone Port')
            pdf.setFont('Helvetica', 12)
            pdf.drawString(150, 700, 'ORDER ID:')
            pdf.drawString(250, 700, str(order_id))

            pdf.line(230, 697, 330, 697)

            pdf.drawString(350, 700, 'QUANTITY:')
            pdf.drawString(500, 700, str(quantity))
            pdf.line(450, 697, 580, 697)

            pdf.drawString(30, 625, 'RECEIVED BY:')
            pdf.line(120, 620, 450, 620)
            pdf.drawString(120, 625, account_name)
            pdf.drawString(350, 673, 'PRIORITY:')
            pdf.drawString(500, 673, priority)
            pdf.line(450, 670, 580, 670)
            pdf.drawString(30, 575, 'DESTINATION: ')
            pdf.line(120, 570, 580, 570)
            pdf.drawString(120, 575, location_name)
            pdf.showPage()
            pdf.save()
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=shippingLabel.pdf'
            return response


    def updateStatus(request):
        order_objects = Order.objects.filter(status="Processing by Warehouse").values('id') \
                            .order_by('priority', 'orderedDatetime', 'id', 'weight')[:1]
        for order_obj in order_objects:
            order_id = int(order_obj['id'])
        Order.objects.filter(id=order_id).update(status="Queued for Dispatch", processedDatetime=timezone.now())
        return redirect("/WHP/main")
