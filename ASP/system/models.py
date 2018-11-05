import datetime

from django.db import models
from django.utils import timezone
# Create your models here.

class Supply(models.Model):
	name = models.CharField(max_length=200)
	category = models.CharField(max_length=200)
	description = models.CharField(max_length=200)
	detail = models.CharField(max_length=200)
	image = models.CharField(max_length=200)
	weight = models.FloatField()
	def __str__(self):
		return self.name

class Order(models.Model):
	status = models.CharField(max_length=30,choices=(('Queued for Processing','Queued for Processing'),
	(' Processing by Warehouse',' Processing by Warehouse'),
	('Queued for Dispatched','Queued for Dispatched'),
	('Dispatched','Dispatched'),
	('Delivered','Delivered')),default='Queued for Processing')
	priority = models.CharField(max_length=4,choices=(('High','high'),('Medium','mid'),('Low','low'),),default='Low')
	orderedDatetime = models.DateTimeField()
	dispatchedDatetime = models.DateTimeField()
	deliveredDatetime = models.DateTimeField()
	weight = models.FloatField()
	def __str__(self):#return order ID as length 8
		temp = str(self.pk)
		string = "Order "
		for i in range(8-len(temp)):
			string = string + "0"
		return string + temp

class Location(models.Model):
	name = models.CharField(max_length=200)
	latitude = models.FloatField()
	longtitude = models.FloatField()
	altitude = models.FloatField()
	def __str__(self):
		return self.name

class Account(models.Model):
	username = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	firstname = models.CharField(max_length=200)
	lastname = models.CharField(max_length=200)
	email = models.EmailField()
	def __str__(self):
		return self.lastname + self.firstname

class CMAccount(models.Model):
	# Clinic Manager Account.
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)

	def __str__(self):
		return self.account.__str__() + " from " + self.location.__str__()

class DispatcherAccount(models.Model):
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	warehouse = models.ForeignKey(Location, on_delete=models.CASCADE)

	def __str__(self):
		return self.account.__str__() + " work at " + self.location.__str__()


class PackerAccount(models.Model):
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	warehouse = models.ForeignKey(Location, on_delete=models.CASCADE)

	def __str__(self):
		return self.account.__str__() + " work at " + self.location.__str__()

#record supply in an order
#different supply in the same order should divide into several records in this table
class Include(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	supply = models.ForeignKey(Supply, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	def __str__(self):
		return "Order " + str(self.order.__str__()) + " includes " + self.supply.__str__()

#the location the order will be delivered to 
class OrderTo(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	def __str__(self):
		return "Order " + str(self.order.__str__()) + " to " + self.location.__str__()

#who order the supply
class OrderBy(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	account = models.ForeignKey(CMAccount, on_delete=models.CASCADE)
	def __str__(self):
		return "Order " + str(self.order.__str__()) + " by " + self.account.__str__()
	

class Distance(models.Model):
	distanceFrom = models.ForeignKey(Location, on_delete=models.CASCADE)
	distanceTo = models.ForeignKey(Location, on_delete=models.CASCADE,related_name="distanceTo")
	distance = models.FloatField()
	def __str__(self):
		return self.distanceFrom.__str__() + " to " + self.distanceTo.__str__()