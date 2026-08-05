from django.urls import path

from . import views

app_name = "chatbot"

urlpatterns = [
    # 채팅 페이지
    path(
        "",
        views.chat_page,
        name="chat",
    ),

    # 새 대화방을 생성하면서 첫 메시지 전송
    path(
        "conversations/messages/stream/",
        views.chat_stream,
        name="chat-stream-new",
    ),

    # 기존 대화방에 이어서 메시지 전송
    path(
        "conversations/<uuid:conversation_id>/messages/stream/",
        views.chat_stream,
        name="chat-stream",
    ),

    # 사이드바용 최근 대화 목록
    path(
        "conversations/",
        views.conversation_list,
        name="conversation-list",
    ),

    # GET: 특정 대화방 메시지 조회
    # DELETE: 특정 대화방과 연결된 메시지 삭제
    path(
        "conversations/<uuid:conversation_id>/messages/",
        views.conversation_messages,
        name="conversation-messages",
    ),
]