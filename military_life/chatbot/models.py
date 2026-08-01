import uuid

from django.conf import settings
from django.db import models


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or f"Conversation {self.id}"

    @property
    def thread_id(self) -> str:
        """LangGraph checkpointer용 thread_id로 그대로 사용."""
        return str(self.id)


class Message(models.Model):
    class Role(models.TextChoices):
        HUMAN = "human", "Human"
        AI = "ai", "AI"
        TOOL = "tool", "Tool"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    references = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.role}] {self.content[:30]}"


class ChatTopic(models.Model):
    """사이드바에 보여줄 FAQ 주제(카테고리). 관리자가 미리 등록."""

    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class FAQ(models.Model):
    """주제 밑에 딸린 질문 하나. 클릭하면 이 question 텍스트가
    사용자 메시지처럼 그대로 챗봇에 전송돼서 실시간으로 답변을 받는다."""

    topic = models.ForeignKey(ChatTopic, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.question