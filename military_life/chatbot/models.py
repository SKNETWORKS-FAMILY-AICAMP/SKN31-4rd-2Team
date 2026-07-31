from django.conf import settings
from django.db import models

class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversation") # 대화방 주인
    title = models.CharField(max_length=200) # 사이드바에 뜨는 대화 제목(ex. "연가 거부 대응 방법")
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.title

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages") # 어느 대화방에 속한 메시지인지
    role = models.CharField(max_length=10) # 메시지를 쓴 게 사용자인지 챗봇인지("user" / "assistant")
    content = models.TextField() # 실제 대화 텍스트
    detail_data = models.JSONField(null=True, blank=True) # "자세히 보기" 눌렀을 때 펼쳐지는 근거, source 등
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        preview = self.content[:20] + ("..." if len(self.content) > 20 else "")
        return f"[{self.role}] {preview}"

class ChatTopic(models.Model):
    name = models.CharField(max_length=50) # 사이드바에 보이는 주제 이름
    order = models.PositiveIntegerField(default=0) # 화면에 보여줄 순서

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name

class FAQ(models.Model):
    topic = models.ForeignKey(ChatTopic, on_delete=models.CASCADE, related_name="faqs") # 질문이 어느 주제에 속하는지
    question = models.CharField(max_length=200) # 실제 버튼에 표시되고, 클릭 시 챗봇에게 자동 전송될 질문 문장(ex. "군별 정기휴가 일수는?")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question