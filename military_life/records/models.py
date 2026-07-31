from django.conf import settings
from django.db import models
from chatbot.models import Message

class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries")
    content = models.TextField() # 일지 내용
    entry_date = models.DateField() # 일지 작성 날짜

    def __str__(self):
        return f"{self.user} - {self.entry_date}"

class Goal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=200) # 목표명
    target_date = models.DateField() # 목표 이룰 날짜
    is_done = models.BooleanField(default=False) # 목표 완료 여부 체크박스 값

    def __str__(self):
        return f"{self.title} ({'완료' if self.is_done else '진행중'})"

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="bookmarks") # 저장된 챗봇 답변이 어떤 메시지인지
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bookmark by {self.user} - {self.message}"