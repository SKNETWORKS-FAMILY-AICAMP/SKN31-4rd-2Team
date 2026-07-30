from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50) # 카테고리 이름("휴가", "징계" 등)

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts") # 작성자
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="posts") # 게시글 카테고리
    title = models.CharField(max_length=200) # 제목
    content = models.TextField() # 본문
    created_at = models.DateTimeField(auto_now_add=True) # 게시글 작성 시각

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments") # 댓글이 달린 게시글
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 작성자
    content = models.TextField() # 댓글 내용
    created_at = models.DateTimeField(auto_now_add=True) # 댓글 작성 시각

