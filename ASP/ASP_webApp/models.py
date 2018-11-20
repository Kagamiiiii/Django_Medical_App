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
    image = models.CharField(max_length=200)
    # This is float field. Storing floating point
    weight = models.FloatField()

    class Meta:
        verbose_name = 'Supply'
        verbose_name_plural = 'Supplies'


# Location information.
class Location(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    isStartingPoint = models.BooleanField()

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'


class Account(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.EmailField()
    worklocation = models.ForeignKey(Location, on_delete=models.CASCADE, limit_choices_to={'isStartingPoint' : False})
    role = models.CharField(max_length=30, choices=(('Clinic Manager', 'Clinic Manager'),
                                                    ('Dispatcher', 'Dispatcher'),
                                                    ('Warehouse Personnel', 'Warehouse Personnel')))
    token = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'


# This is similar to Enum in MySQL, where the stored data can only be one of the choice in choices option.
class Order(models.Model):
    status = models.CharField(max_length=30, choices=(('Queued for Processing', 'Queued for Processing'),
                                                      ('Processing by Warehouse', 'Processing by Warehouse'),
                                                      ('Queued for Dispatch', 'Queued for Dispatch'),
                                                      ('Dispatched', 'Dispatched'),
                                                      ('Delivered', 'Delivered'),
                                                      ('Cancelled', 'Cancelled')), default='Queued for Processing')
    priority = models.CharField(max_length=10, choices=(('High', 1), ('Medium', 2), ('Low', 3)),
                                default='Low')
    weight = models.FloatField()
    orderedDatetime = models.DateTimeField()
    processedDatetime = models.DateTimeField(blank=True, null=True)
    dispatchedDatetime = models.DateTimeField(blank=True, null=True)
    deliveredDatetime = models.DateTimeField(blank=True, null=True)
    ordering_clinic = models.ForeignKey(Location, on_delete=models.CASCADE, limit_choices_to={'isStartingPoint': False})
    ordering_account = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    @classmethod
    def create(cls, priority, ODatetime, clinic, weight, account):
        order = cls(priority=priority, orderedDatetime=ODatetime, ordering_clinic_id=clinic, weight=weight, ordering_account_id=account)
        return order


# record supply in an order
# different supply in the same order should divide into several records in this table
class Include(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        verbose_name = 'Include'
        verbose_name_plural = 'Includes'
        unique_together = (("order", "supply"),)

    @classmethod
    def create(cls, oid, supply, quantity):
        includes = cls(order=oid, supply=supply, quantity=quantity)
        return includes

# distance data model, should storing the calculation result of distance data for deliveries.
class Distance(models.Model):
    distanceFrom = models.ForeignKey(Location, on_delete=models.CASCADE)
    distanceTo = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="distanceTo")
    distance = models.FloatField()

    class Meta:
        verbose_name = 'Distance'
        verbose_name_plural = 'Distances'
        unique_together = (("distanceFrom", "distanceTo"),)
