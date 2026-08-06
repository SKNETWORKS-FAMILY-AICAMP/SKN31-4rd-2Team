import json

from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from back_logic.chatbot import chatbot
from .models import Conversation, Message

RECENT_CONVERSATION_LIMIT = 10


def _get_user_rank_text(user) -> str:
    """사용자 프로필의 계급을 화면 표시용 문자열로 반환한다."""
    profile = getattr(user, "profile", None)
    if profile is None:
        return ""

    get_rank_display = getattr(profile, "get_rank_display", None)
    if callable(get_rank_display):
        rank_display = get_rank_display()
        if rank_display:
            return str(rank_display).strip()

    rank = getattr(profile, "rank", "")
    return str(rank).strip() if rank is not None else ""


def _build_welcome_message(rank: str) -> str:
    """사용자의 계급에 맞는 새 채팅 인사말을 만든다."""
    normalized_rank = (rank or "").replace(" ", "").upper()

    rank_aliases = {
        "PRIVATE": "이병",
        "PRIVATEFIRSTCLASS": "일병",
        "CORPORAL": "상병",
        "SERGEANT": "병장",
        "STAFFSERGEANT": "하사",
        "SERGEANTFIRSTCLASS": "중사",
        "MASTERSERGEANT": "상사",
        "SERGEANTMAJOR": "원사",
        "SECONDLIEUTENANT": "소위",
        "FIRSTLIEUTENANT": "중위",
        "CAPTAIN": "대위",
        "MAJOR": "소령",
        "LIEUTENANTCOLONEL": "중령",
        "COLONEL": "대령",
        "BRIGADIERGENERAL": "준장",
        "MAJORGENERAL": "소장",
        "LIEUTENANTGENERAL": "중장",
        "GENERAL": "대장",
    }

    display_rank = rank_aliases.get(normalized_rank, rank.strip() if rank else "")

    soldier_ranks = {"이병", "일병", "상병", "병장"}
    nco_ranks = {"하사", "중사", "상사", "원사"}
    officer_ranks = {
        "준위", "소위", "중위", "대위",
        "소령", "중령", "대령",
        "준장", "소장", "중장", "대장",
    }

    if display_rank in soldier_ranks:
        return (
            f"충성! {display_rank}, 박병장 상담소에 잘 왔다. "
            "휴가, 징계, 급여, 전역처럼 군 생활 중 궁금한 건 편하게 물어봐. "
            "형이 규정과 근거를 확인해서 알려줄게!"
        )

    if display_rank in nco_ranks:
        return (
            f"충성! {display_rank}님, 박병장 상담소입니다. "
            "군 법규와 병영생활 관련해 궁금하신 내용을 말씀해 주시면 "
            "규정과 근거를 확인해 안내드리겠습니다."
        )

    if display_rank in officer_ranks:
        return (
            f"충성! {display_rank}님, 박병장 상담소입니다. "
            "군 법규, 복무 규정, 병영생활과 관련해 확인이 필요한 사항을 말씀해 주십시오. "
            "관련 근거를 찾아 정확히 보고드리겠습니다."
        )

    if display_rank:
        return (
            f"안녕하세요, {display_rank}님. 박병장 상담소입니다. "
            "군 법규와 병영생활에 관해 궁금한 내용을 편하게 말씀해 주세요."
        )

    return (
        "안녕! 나는 군 법규랑 병영생활 관련해서 도와주는 박병장이야. "
        "휴가, 징계, 급여, 전역 같은 거 뭐든 편하게 물어봐. 형이 다 알려줄게!"
    )


@login_required
def chat_page(request):
    """채팅 페이지를 렌더링하고 최근 대화 10개를 함께 전달한다."""
    conversations = list(
        Conversation.objects.filter(user=request.user).order_by("-updated_at")[
            :RECENT_CONVERSATION_LIMIT
        ]
    )
    user_rank = _get_user_rank_text(request.user)
    welcome_message = _build_welcome_message(user_rank)

    return render(
        request,
        "chat.html",
        {
            "conversations": conversations,
            "welcome_message": welcome_message,
        },
    )


@login_required
@require_http_methods(["GET"])
def conversation_list(request):
    """로그인한 사용자의 최근 대화 10개를 JSON으로 반환한다."""
    conversations = Conversation.objects.filter(user=request.user).order_by(
        "-updated_at"
    )[:RECENT_CONVERSATION_LIMIT]

    return JsonResponse(
        {
            "conversations": [
                {
                    "id": str(conversation.id),
                    "title": conversation.title or "새 대화",
                }
                for conversation in conversations
            ]
        }
    )


@login_required
@require_http_methods(["GET", "DELETE"])
def conversation_messages(request, conversation_id):
    """
    GET:
        특정 대화방의 메시지 목록을 반환한다.

    DELETE:
        특정 대화방과 그 대화에 연결된 메시지를 삭제한다.

    로그인한 사용자가 소유한 대화만 조회하거나 삭제할 수 있다.
    """
    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user,
        )
    except Conversation.DoesNotExist:
        raise Http404

    if request.method == "DELETE":
        conversation.delete()

        return JsonResponse(
            {
                "success": True,
                "message": "대화가 삭제되었습니다.",
                "conversation_id": str(conversation_id),
            },
            status=200,
        )

    messages = conversation.messages.exclude(role=Message.Role.TOOL).order_by(
        "created_at"
    )

    return JsonResponse(
        {
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                    "references": message.references,
                }
                for message in messages
            ]
        }
    )


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@csrf_exempt
@require_POST
async def chat_stream(request, conversation_id=None):
    """
    새 대화를 생성하거나 기존 대화에 메시지를 추가하고,
    챗봇 답변을 SSE 방식으로 스트리밍한다.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    user_message = (body.get("message") or "").strip()

    if not user_message:
        return JsonResponse({"error": "message is required"}, status=400)

    def _resolve_user_and_rank():
        if not request.user.is_authenticated:
            return None, None, None

        user = request.user
        profile = getattr(user, "profile", None)
        rank = getattr(profile, "rank", None)
        status = getattr(profile, "status", None)  # "간부" 또는 "병사"

        return user, rank, status

    user, user_rank, user_status = await sync_to_async(_resolve_user_and_rank)()

    if user_status is not None:
        prompt_message = f"[질문자 신분: {user_status} / 계급: {user_rank or '미상'}]\n{user_message}"
    else:
        prompt_message = user_message

    is_new_conversation = conversation_id is None

    if conversation_id:
        conversation = await Conversation.objects.filter(
            id=conversation_id,
            user=user,
        ).afirst()

        if conversation is None:
            return JsonResponse(
                {"error": "conversation not found"},
                status=404,
            )
    else:
        conversation = await Conversation.objects.acreate(
            user=user,
            title=user_message[:50],
        )

    history = [
        (message.role, message.content)
        async for message in conversation.messages.exclude(
            role=Message.Role.TOOL
        ).order_by("created_at")
    ]

    await Message.objects.acreate(
        conversation=conversation,
        role=Message.Role.HUMAN,
        content=user_message,
    )

    async def event_stream():
        yield _sse(
            {
                "type": "meta",
                "conversation_id": str(conversation.id),
            }
        )

        final_content = ""
        references: list[str] = []

        try:
            async for event in chatbot.astream(
                prompt_message,
                history,
                conversation.thread_id,
            ):
                if event["type"] == "token":
                    yield _sse(
                        {
                            "type": "token",
                            "content": event["content"],
                        }
                    )

                elif event["type"] == "tool_start":
                    yield _sse(
                        {
                            "type": "tool_start",
                            "tool": event["tool"],
                        }
                    )

                elif event["type"] == "tool_end":
                    yield _sse(
                        {
                            "type": "tool_end",
                            "tool": event["tool"],
                        }
                    )

                elif event["type"] == "done":
                    final_content = event["content"]
                    references = event["references"]

        except Exception as exc:  # noqa: BLE001
            yield _sse(
                {
                    "type": "error",
                    "message": str(exc),
                }
            )
            return

        await Message.objects.acreate(
            conversation=conversation,
            role=Message.Role.AI,
            content=final_content,
            references=references,
        )

        update_fields = ["updated_at"]

        if is_new_conversation:
            conversation.title = await chatbot.agenerate_title(user_message)
            update_fields.append("title")

        await conversation.asave(update_fields=update_fields)

        yield _sse({"type": "done"})

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"

    return response