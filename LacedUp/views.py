from django.shortcuts import render,redirect
from django.http import HttpResponse
from category.models import Category

def home(request):
    categories = Category.objects.all()
    return render(request, 'Home.html', {'categories': categories})