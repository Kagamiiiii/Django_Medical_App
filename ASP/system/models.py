"""
This page defines all models in Django: it means the data model in the database in Django.
In this case we're using SQLite 3, a very different database than MySQL.
SQLite 3 is file based, and provide super light weight interaction.
It doesn't offer high security feature like in MySQL, but it offers to ability to write/read data
from disk directly.

This data model should be designed with Class Model/ Diagram, and use some abbreviation related to the names
we've used in the documents to avoid confusion.
"""
import datetime

from django.db import models
from django.utils import timezone


# Create your models here.


class Supply(models.Model):
    # These defines the data model in the database.
    # This is a common data type CharField.
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    detail = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    # This is float field. Storing floating point
    weight = models.FloatField()

    # this function return a human readable string about this data model upon call.
    def __str__(self):
        return self.name


# Location information.
class Location(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
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


# Clinic Manager Account.
class CMAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.account.__str__() + " from " + self.location.__str__()


# account for dispatcher
class DispatcherAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.account.__str__() + " work at " + self.location.__str__()


# account for warehouse personnel
class WHPAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.account.__str__() + " work at " + self.location.__str__()


# This is similar to Enum in MySQL, where the stored data can only be one of the choice in choices option.
class Order(models.Model):
    status = models.CharField(max_length=30, choices=(('Queued for Processing', 'Queued for Processing'),
                                                      (' Processing by Warehouse', ' Processing by Warehouse'),
                                                      ('Queued for Dispatched', 'Queued for Dispatched'),
                                                      ('Dispatched', 'Dispatched'),
                                                      ('Delivered', 'Delivered')), default='Queued for Processing')
    priority = models.CharField(max_length=4, choices=(('High', 'high'), ('Medium', 'mid'), ('Low', 'low'),),
                                default='Low')
    ordering_clinic = models.ForeignKey(Location, on_delete=models.CASCADE)
    # This defines some DateTimeField type objects in SQLite 3
    orderedDatetime = models.DateTimeField()
    dispatchedDatetime = models.DateTimeField()
    deliveredDatetime = models.DateTimeField()
    weight = models.FloatField()
    items = models.TextField()
    CMid = models.ForeignKey(CMAccount, on_delete=models.CASCADE)

    # returns an order ID of length 8
    # the order starts from 00000001.
    def __str__(self):
        temp = str(self.pk)
        string = "Order "
        for i in range(8 - len(temp)):
            string += "0"
        return string + temp

    @classmethod
    def create(cls, priority, items, ODatetime, cid, weight):
        order = cls(priority=priority, items=items, orderedDatetime=ODatetime, ordering_clinic=cid, weight=weight)
        return order


# record supply in an order
# different supply in the same order should divide into several records in this table
class Include(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return "Order " + str(self.order.__str__()) + " includes " + self.supply.__str__()


# records the location the order will be delivered to
class OrderTo(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return "Order " + str(self.order.__str__()) + " to " + self.location.__str__()


# records which clinic manager has ordered the supply
class OrderBy(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    account = models.ForeignKey(CMAccount, on_delete=models.CASCADE)

    def __str__(self):
        return "Order " + str(self.order.__str__()) + " by " + self.account.__str__()


# distance data model, should storing the calculation result of distance data for deliveries.
class Distance(models.Model):
    distanceFrom = models.ForeignKey(Location, on_delete=models.CASCADE)
    distanceTo = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="distanceTo")
    distance = models.FloatField()

    def __str__(self):
        return self.distanceFrom.__str__() + " to " + self.distanceTo.__str__()
