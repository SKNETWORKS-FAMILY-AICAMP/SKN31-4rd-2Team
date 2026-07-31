from django.shortcuts import render
from django.http import HttpResponse

def login_view(request):
    return HttpResponse("로그인 페이지 (임시)")

def signup_view(request):
    return HttpResponse("회원가입 페이지 (임시)")

def logout_view(request):
    return HttpResponse("회원가입 페이지 (임시)")