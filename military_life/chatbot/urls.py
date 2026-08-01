from django.urls import path

from . import views

app_name = "chatbot"  # base.html에서 {% url 'chatbot:chat' %} 식으로 참조하니까 필요

urlpatterns = [
    # 채팅 페이지 - base.html이 'chatbot:chat'이라는 이름으로 참조함
    path("", views.chat_page, name="chat"),
    # 새 대화방 시작하면서 첫 메시지 전송
    path("conversations/messages/stream/", views.chat_stream, name="chat-stream-new"),
    # 기존 대화방에 이어서 메시지 전송
    path(
        "conversations/<uuid:conversation_id>/messages/stream/",
        views.chat_stream,
        name="chat-stream",
    ),
]