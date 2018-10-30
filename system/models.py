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
	def __str__(self):
		return self.name

class Order(models.Model):
	status = models.CharField(max_length=200)
	priority = models.CharField(max_length=4,choices=(('High','high'),('Medium','mid'),('Low','low'),),default='Low')
	orderedDatetime = models.DateTimeField()
	dispatchedDatetime = models.DateTimeField()
	deliveredDatetime = models.DateTimeField()
	def __str__(self):
		return "Order " + str(self.pk)

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
	position = models.CharField(max_length=200)
	def __str__(self):
		return self.lastname + self.firstname

class Include(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	supply = models.ForeignKey(Supply, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	def __str__(self):
		return "Order " + str(self.order.__str__()) + " includes " + self.supply.__str__()

class OrderTo(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	def __str__(self):
		return "Order " + str(self.order.__str__()) + " to " + self.location.__str__()

class OrderBy(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	def __str__(self):
		return "Order " + str(self.order.__str__()) + " by " + self.account.__str__()
 
class AccountFrom(models.Model):
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	def __str__(self):
		return self.account.__str__() + " from " + self.location.__str__()

class Distance(models.Model):
	distanceFrom = models.ForeignKey(Location, on_delete=models.CASCADE)
	distanceTo = models.ForeignKey(Location, on_delete=models.CASCADE,related_name="distanceTo")
	distance = models.FloatField()
	def __str__(self):
		return self.distanceFrom.__str__() + " to " + self.distanceTo.__str__()