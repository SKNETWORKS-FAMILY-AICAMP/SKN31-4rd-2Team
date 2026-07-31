from django.shortcuts import render
from django.http import HttpResponse

def records(request):
    return HttpResponse("기록 페이지 (임시)")
