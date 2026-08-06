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

class Report(models.Model):
    """
    게시글 신고 내역을 저장하는 모델입니다.
    어느 사용자가 어떤 게시글을 무슨 사유로 신고했는지 기록합니다.
    """
    STATUS_CHOICES = (
        ('PENDING', '대기중'),
        ('RESOLVED', '처리완료'),
        ('REJECTED', '반려'),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports") # 신고된 게시글
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reports") # 신고자
    reason = models.TextField() # 신고 사유
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING') # 처리 상태
    created_at = models.DateTimeField(auto_now_add=True) # 신고 일시

    class Meta:
        unique_together = ("post", "reporter") # 중복 신고 방지

    def __str__(self):
        return f"Report by {self.reporter} on {self.post}"

from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Report)
def delete_post_on_report_delete(sender, instance, **kwargs):
    """
    신고 내역(Report)이 삭제될 때, 해당 신고가 연결된 원본 게시글(Post)도 함께 삭제합니다.
    (Post.objects.filter.delete()를 사용하여 연쇄 삭제(Cascade) 충돌을 방지합니다.)
    """
    if instance.post_id:
        Post.objects.filter(id=instance.post_id).delete()