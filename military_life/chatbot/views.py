import json

from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from back_logic.chatbot import chatbot
from .models import Conversation, Message

RECENT_CONVERSATION_LIMIT = 10


@login_required
def chat_page(request):
    """채팅 페이지 (chat.html) 렌더링. 사이드바용 최근 대화 10개도 같이 내려준다."""
    conversations = list(
        Conversation.objects.filter(user=request.user).order_by("-updated_at")[
            :RECENT_CONVERSATION_LIMIT
        ]
    )
    return render(request, "chat.html", {"conversations": conversations})


def conversation_list(request):
    """사이드바 갱신용 - 로그인한 사용자의 최근 대화 10개 (JSON)."""
    if not request.user.is_authenticated:
        return JsonResponse({"conversations": []})

    conversations = Conversation.objects.filter(user=request.user).order_by(
        "-updated_at"
    )[:RECENT_CONVERSATION_LIMIT]

    return JsonResponse(
        {
            "conversations": [
                {"id": str(c.id), "title": c.title or "새 대화"} for c in conversations
            ]
        }
    )


def conversation_messages(request, conversation_id):
    """특정 대화방의 메시지 목록 (JSON). 본인 대화만 조회 가능."""
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        raise Http404

    owner_id = conversation.user_id
    requester_id = request.user.id if request.user.is_authenticated else None
    if owner_id is None or owner_id != requester_id:
        raise Http404  # 남의 대화방은 못 봄

    messages = conversation.messages.exclude(role=Message.Role.TOOL).order_by(
        "created_at"
    )
    return JsonResponse(
        {
            "messages": [
                {"role": m.role, "content": m.content, "references": m.references}
                for m in messages
            ]
        }
    )


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

    # request.user는 SimpleLazyObject라서 ".is_authenticated"나 ".rank"처럼
    # 실제 속성을 건드리는 순간 세션/DB 조회(동기)가 일어난다.
    # 그 "건드리는 순간"이 sync_to_async 안에서 일어나야 스레드에서 안전하게 처리됨.
    def _resolve_user_and_rank():
        if not request.user.is_authenticated:
            return None, None
        u = request.user
        rank = getattr(getattr(u, "profile", None), "rank", None)
        return u, rank

    user, user_rank = await sync_to_async(_resolve_user_and_rank)()

    # LLM에 넘길 prompt에만 계급 정보를 붙인다 (저장되는 메시지 원문은 그대로 유지)
    if user_rank is not None:
        prompt_message = f"질문자 계급[{user_rank}]\n{user_message}"
    else:
        prompt_message = user_message

    is_new_conversation = conversation_id is None

    if conversation_id:
        conversation = await Conversation.objects.filter(id=conversation_id).afirst()
        if conversation is None:
            return JsonResponse({"error": "conversation not found"}, status=404)
    else:
        # 일단 원문 잘라서 임시 제목으로 저장 -> 첫 답변 끝나면 LLM 요약본으로 교체
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
            async for event in chatbot.astream(prompt_message, history, conversation.thread_id):
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

        update_fields = ["updated_at"]
        if is_new_conversation:
            # 첫 턴에서만 - 임시 제목(원문 자른 것)을 LLM 요약 제목으로 교체
            conversation.title = await chatbot.agenerate_title(user_message)
            update_fields.append("title")

        # updated_at을 갱신해야 사이드바에서 "방금 대화한 순서"대로 정렬됨.
        # (안 해주면 Conversation.updated_at이 생성 시점에 멈춰있음)
        await conversation.asave(update_fields=update_fields)
        yield _sse({"type": "done"})

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # nginx 프록시 쓸 때 버퍼링 막기
    return response