import datetime

from django import template
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.template.loader import render_to_string

register = template.Library()


