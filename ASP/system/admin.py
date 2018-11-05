from django.contrib import admin
from .models import Supply,Order,Location,Account,Include,OrderTo,OrderBy,HAAccount,DispatcherAccount,PackerAccount,Distance

#this affects the view of record in database at django admin page
#an admin user should be created 
#account: admin 
#password: admin

class SupplyAdmin(admin.ModelAdmin):
    list_display = ('name','category','description','weight','detail','image')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('status','priority','weight','orderedDatetime','dispatchedDatetime','deliveredDatetime')
	
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name','latitude','longtitude','altitude')
	
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username','password','firstname','lastname','email')
	
class IncludeAdmin(admin.ModelAdmin):
    list_display = ('order','supply','quantity')
	
class OrderToAdmin(admin.ModelAdmin):
    list_display = ('order','location')
	
class OrderByAdmin(admin.ModelAdmin):
    list_display = ('order','account')
	
class HAAccountAdmin(admin.ModelAdmin):
    list_display = ('account','location')
	
class DispatcherAccountAdmin(admin.ModelAdmin):
    list_display = ('account','warehouse')
	
class PackerAccountAdmin(admin.ModelAdmin):
    list_display = ('account','warehouse')
	
class DistanceAdmin(admin.ModelAdmin):
    list_display = ('distanceFrom','distanceTo','distance')

# Register your models here.
admin.site.register(Supply,SupplyAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Location,LocationAdmin)
admin.site.register(Account,AccountAdmin)
admin.site.register(Include,IncludeAdmin)
admin.site.register(OrderTo,OrderToAdmin)
admin.site.register(OrderBy,OrderByAdmin)
admin.site.register(HAAccount,HAAccountAdmin)
admin.site.register(DispatcherAccount,DispatcherAccountAdmin)
admin.site.register(PackerAccount,PackerAccountAdmin)
admin.site.register(Distance,DistanceAdmin)