import json

from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from back_logic.chatbot import chatbot
from .models import Conversation, Message


def chat_page(request):
    """채팅 페이지 (chat.html) 렌더링."""
    return render(request, "chat.html")


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@csrf_exempt  # TODO: 로그인 붙으면 세션 인증 + CSRF 토큰(fetch 헤더) 방식으로 교체
@require_POST
async def chat_stream(request, conversation_id=None):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    user_message = (body.get("message") or "").strip()
    if not user_message:
        return JsonResponse({"error": "message is required"}, status=400)

    user = request.user if request.user.is_authenticated else None

    if conversation_id:
        conversation = await Conversation.objects.filter(id=conversation_id).afirst()
        if conversation is None:
            return JsonResponse({"error": "conversation not found"}, status=404)
    else:
        conversation = await Conversation.objects.acreate(user=user, title=user_message[:50])

    # 새 사용자 메시지를 저장하기 "전"에 history를 먼저 읽어서
    # 방금 보낸 질문이 history에 중복으로 안 들어가게 한다.
    history = [
        (m.role, m.content)
        async for m in conversation.messages.exclude(role=Message.Role.TOOL).order_by("created_at")
    ]

    await Message.objects.acreate(
        conversation=conversation, role=Message.Role.HUMAN, content=user_message
    )

    async def event_stream():
        yield _sse({"type": "meta", "conversation_id": str(conversation.id)})

        final_content = ""
        references: list[str] = []

        try:
            async for event in chatbot.astream(user_message, history, conversation.thread_id):
                if event["type"] == "token":
                    yield _sse({"type": "token", "content": event["content"]})
                elif event["type"] == "tool_start":
                    yield _sse({"type": "tool_start", "tool": event["tool"]})
                elif event["type"] == "tool_end":
                    yield _sse({"type": "tool_end", "tool": event["tool"]})
                elif event["type"] == "done":
                    final_content = event["content"]
                    references = event["references"]
        except Exception as exc:  # noqa: BLE001
            yield _sse({"type": "error", "message": str(exc)})
            return

        await Message.objects.acreate(
            conversation=conversation,
            role=Message.Role.AI,
            content=final_content,
            references=references,
        )
        yield _sse({"type": "done"})

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # nginx 프록시 쓸 때 버퍼링 막기
    return response