from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import *


# this affects the view of record in database at django admin page
# an admin user should be created
# account: admin
# password: admin

class SupplyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'weight', 'image')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'altitude')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('status', 'priority', 'weight', 'orderedDatetime', 'dispatchedDatetime', 'deliveredDatetime')


class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'firstname', 'lastname', 'email', 'worklocation', 'role')


class IncludeAdmin(admin.ModelAdmin):
    list_display = ('order', 'supply', 'quantity')


class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ('order', 'location', 'account')


class DistanceAdmin(admin.ModelAdmin):
    list_display = ('distanceFrom', 'distanceTo', 'distance')


# Register your models here.
admin.site.register(Supply, SupplyAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Include, IncludeAdmin)
admin.site.register(OrderInfo, OrderInfoAdmin)
admin.site.register(Distance, DistanceAdmin)