import datetime

from django import template
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from rest_framework import generics

from users.forms import CustomCreationForm


@login_required
def home(request):
    return render(request, 'sites/home.html')

def signup(request):
    if request.method == 'POST':
        form = CustomCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })
