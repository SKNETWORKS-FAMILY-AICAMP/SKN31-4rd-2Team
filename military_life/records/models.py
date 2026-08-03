from django.conf import settings
from django.db import models
from chatbot.models import Message

class JournalEntry(models.Model): # 캘린더
    class EntryType(models.TextChoices):
        GENERAL = "일반", "일반"
        LEAVE = "휴가", "휴가"
        OVERNIGHT = "외박", "외박"
        OUTING = "외출", "외출"

    class Mood(models.TextChoices):
        HAPPY = "행복", "😊"
        NEUTRAL = "보통", "😐"
        TIRED = "지침", "😔"
        WORKOUT = "운동", "💪"
        STUDY = "학습", "📚"
        SLEEPY = "졸림", "😴"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries")
    entry_type = models.CharField(max_length=10, choices=EntryType.choices, default=EntryType.GENERAL) # 일정 유형(일반/휴가/외박/외출) - 캘린더 화면 반영
    mood = models.CharField(max_length=10, choices=Mood.choices, null=True, blank=True) # 오늘의 기분 - 캘린더 화면 반영
    content = models.TextField(blank=True) # 일지 내용(메모)
    entry_date = models.DateField() # 일지 작성 날짜

    class Meta:
        unique_together = ("user", "entry_date") # 하루에 하나의 기록만 작성(같은 날짜 재저장 시 덮어쓰기)

    def __str__(self):
        return f"{self.user} - {self.entry_date} ({self.entry_type})"

class Goal(models.Model): # 목표
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    category = models.CharField(max_length=50, blank=True) # 목표 카테고리("자격증", "체력", "어학" 등) 
    title = models.CharField(max_length=200) # 목표명
    progress = models.PositiveIntegerField(default=0) # 달성률(%) - 진행률 바
    target_date = models.DateField() # 목표 이룰 날짜
    is_done = models.BooleanField(default=False) # 목표 완료 여부 체크박스 값

    def __str__(self):
        return f"{self.title} ({self.progress}% 달성)"

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="bookmarks") # 저장된 챗봇 답변이 어떤 메시지인지
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bookmark by {self.user} - {self.message}"