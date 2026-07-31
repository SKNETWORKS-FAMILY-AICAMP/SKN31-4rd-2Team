from django.contrib import admin
from .models import Conversation, Message, ChatTopic, FAQ

admin.site.register(Conversation)
admin.site.register(Message)

# 사이드바 FAQ 질문: 관리자가 미리 등록해두는 콘텐츠
## 관리자 화면에서 주제 하나 열었을 때 그 밑에 딸린 질문들 바로 추가/수정 가능
class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1

@admin.register(ChatTopic)
class ChatTopicAdmin(admin.ModelAdmin):
    inlines = [FAQInline]
