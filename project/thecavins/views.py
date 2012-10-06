# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.http import HttpResponse
from django.conf import settings

def homepage(request):
    return render(request, 'thecavins/homepage.html')
    
