from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def download(reuest):
    return HttpResponse("Hellow word")