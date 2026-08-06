from django.contrib import admin
from .models import Category, Post, Comment, PostLike, Report

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostLike)
admin.site.register(Report)