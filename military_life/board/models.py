from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50) # 카테고리 이름("휴가", "징계" 등)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts") # 작성자
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="posts") # 게시글 카테고리
    title = models.CharField(max_length=200) # 제목
    content = models.TextField() # 본문
    view_count = models.PositiveIntegerField(default=0) # 조회수 - 게시판 화면의 조회수 표시 반영
    created_at = models.DateTimeField(auto_now_add=True) # 게시글 작성 시각

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments") # 댓글이 달린 게시글
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 작성자
    content = models.TextField() # 댓글 내용
    created_at = models.DateTimeField(auto_now_add=True) # 댓글 작성 시각

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes") # 좋아요가 눌린 게시글
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_likes") # 좋아요를 누른 사용자
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user") # 중복 좋아요 제한

    def __str__(self):
        return f"{self.user} likes {self.post}"