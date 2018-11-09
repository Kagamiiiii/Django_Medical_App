from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import *
from django.utils import timezone
from .models import Supply
import json

# Create your views here.


# if not use generic view, use render to call html
# cat is the category name
def displayByCategory(request, cat):
    supply = Supply.objects.filter(category=cat)
    list = {'supply':supply}
    return list

