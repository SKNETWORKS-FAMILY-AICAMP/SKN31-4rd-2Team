from django.shortcuts import render
from django.http import HttpResponse

def post_list(request):
    return HttpResponse("게시글 페이지 (임시)")

def post_create(request):
    return HttpResponse("작성 페이지 (임시)")
