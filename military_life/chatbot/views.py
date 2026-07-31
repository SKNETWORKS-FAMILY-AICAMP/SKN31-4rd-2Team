from django.shortcuts import render
from django.http import HttpResponse

def chat(request):
    return HttpResponse("챗봇 페이지 (임시)")

def send_message(request):
    return HttpResponse("메시지 (임시)")

