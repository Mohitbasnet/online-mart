from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product,OrderItem
from django.db.models import Q,F
from django.core.mail import EmailMessage, BadHeaderError
from templated_mail.mail import BaseEmailMessage
from . tasks import notify_customers
def say_hello(request):
    notify_customers.delay('Hello')
    
    return render(request, 'hello.html',{'name': 'Mohit'})
