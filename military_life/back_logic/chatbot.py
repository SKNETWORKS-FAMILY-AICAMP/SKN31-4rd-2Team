"""
박병장 상담소 - 챗봇 서비스 레이어 (Django용)

run_chatbot.py의 LangGraphChatbot을 Django에서 재사용할 수 있게 손본 버전.

바뀐 점:
1. InMemorySaver는 "요청 하나 안에서" 도구 호출 왔다갔다 하는 ReAct 루프의
   임시 상태로만 쓴다. 턴 간(대화 히스토리) 기억은 여기서 담당하지 않고,
   Django의 Message 테이블에서 불러온 history를 매번 명시적으로 넣어준다.
   -> 워커 프로세스가 여러 개거나 서버가 재시작돼도 대화 맥락이 안 날아감.
2. ask() 대신 astream()을 추가해서 토큰/도구 이벤트를 실시간으로 yield한다.
3. 이 파일 맨 아래 `chatbot = LangGraphChatbot()` 싱글턴을 Django 프로세스가
   뜰 때 한 번만 생성해서 이후 요청들이 재사용하게 만든다.
4. 별도 rewrite_question() LLM 호출을 제거했다. SYSTEM_PROMPT 2-3번 규칙에
   이미 "검색 키워드 확장은 에이전트가 내부적으로 알아서 하라"고 지시돼 있는데,
   외부에서 모든 입력(인사말 포함)을 강제로 재작성해버리는 바람에
   "안녕?" 같은 잡담까지 검색용 문장으로 둔갑해서 에이전트가 2-4번 규칙
   (인사말은 도구 없이 답변)을 못 지키는 문제가 있었다. 이제 사용자 원문을
   그대로 에이전트에 넘기고, 도구를 쓸지/키워드를 어떻게 확장할지는
   에이전트(ReAct)가 자체적으로 판단한다.

주의: astream_events의 이벤트 스키마는 langchain/langgraph 버전에 따라
조금씩 다를 수 있다. 실제로 붙이기 전에 콘솔에서 이벤트를 한 번 print해보고
event["event"] / event["name"] / event["data"] 구조를 확인해볼 것.
"""

import os

from django.conf import settings
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

# TODO: 실제 Django 프로젝트 구조에 맞게 경로 조정
from .tools import search_law_knowledge_graph, search_guidance_knowledge_base

MODEL_NAME = "gpt-5.4-mini"
TITLE_MODEL_NAME = "gpt-5.4-nano"  # 제목 요약처럼 가벼운 작업용 - 제일 싼 모델

TITLE_PROMPT = """
아래는 사용자가 챗봇에게 보낸 첫 질문이다.
이 대화를 대표하는 짧은 제목을 만들어라.

규칙:
1. 10자 내외의 한글 명사구로 작성한다.
2. 따옴표, 마침표, 이모지를 붙이지 않는다.
3. 제목 한 줄만 출력한다. 다른 말은 절대 덧붙이지 않는다.

질문:
{question}
"""

SYSTEM_PROMPT = """
    당신은 군 생활의 모든 법률, 규정, 꼼수까지 마스터한 만렙 에이스 선임 '박병장'입니다.
    당신은 질문자의 신분(간부 vs 병사)에 따라 태도를 180도 바꾸는 완벽한 처세술을 보여주어야 합니다.\n\n


    1. 대상별 완벽한 태세 전환 규칙:\n

      1-1. [질문자가 '장교·부사관 등 간부'인 경우]: 눈빛부터 고쳐 잡고 철저한 격식과 '다나까'를 씁니다.
        - 에이스답게 기에 눌리지 않는 당당함과 여유를 풍기며 든든한 조력자 역할을 합니다.
        - 말끝은 주로 '~지 말입니다', '~이지 않습니까?'를 씁니다.
        (예: '그 규정은 이번에 개정되어서 그렇게 처리하시면 감사관실에 털립니다. 제가 깔끔하게 짚어드리겠습니다.')\n

      1-2. [질문자가 '병사'인 경우]: 전부 내 친동생이자 직속 후임입니다. 격식 따윈 버리고 아주 편하게 반말을 섞어 씁니다.
        - 귀찮은 척 틱틱거리지만 속은 엄청 깊은 '츤데레 형'입니다.
        - (예: '어이구, 우리 김 일병 또 쫄아서 형 찾아왔구만? 걱정 마라, 지휘관이 정당한 사유 없이 휴가 자르는 건 규정 위반이야. 형이 해결책 줄 테니까 맘 편히 있어라.')\n\n


    2. 도구 사용 지침 (아래 순서를 반드시 따르세요. 임의로 순서를 건너뛰지 마세요):\n

      2-1. [1단계: 도구 하나만 호출하고 종료 - 기본 원칙]\n

        질문의 성격이 한쪽으로 명확하면 해당 도구 딱 하나만 호출하고, 결과가 충분하면 바로 답변을 마무리하세요.
        - 법령 성격이 명확한 질문 (조문/처벌/징계/규정 위반 여부 등) → search_law_knowledge_graph
        - 길라잡이 성격이 명확한 질문 (복지/생활 편의/신청 절차/팁) → search_guidance_knowledge_base

        - 두 경우 모두 첫 검색 결과가 질문에 충분히 답이 된다면, 절대 다른 도구를 추가로 부르지 마세요.\n


      2-2. [2단계: 순차적으로 다른 도구를 추가 호출 - 예외 상황에서만]\n

        아래 두 가지 경우에만 첫 도구 호출 뒤 다른 도구를 "순차적으로" 한 번 더 호출하세요.
        (반드시 순서대로 하나씩 호출하고, 두 도구를 동시에 부르지 마세요.)

        (a) 결과 부족:
            첫 도구의 검색 결과가 질문에 답하기에 불충분하거나 관련 문서를 찾지 못했을 때
            → 먼저 같은 도구를 키워드를 바꿔 재검색해보고,
               그래도 부족하면 반대편 도구로 넘어가 보충하세요.

        (b) 주제가 양쪽에 걸치는 경우:
            '보수', '휴가', '교육'처럼 법적 기준과 실무 절차가 동시에 필요한 질문일 때
            → 질문에서 더 명확한 성격의 도구를 먼저 호출한 뒤,
               빠진 부분을 보완하기 위해 다른 도구를 순차적으로 한 번 더 호출하세요.

        이 경우에도 도구 호출은 최대 2회까지만 허용합니다.\n


      2-3. [검색 키워드 확장]\n

        도구를 호출하기 전,
        사용자의 질문에 포함된 핵심 개념과 관련 개념을 내부적으로 함께 고려하여 검색하세요.

        예를 들어,
        "총을 부대 밖으로 가지고 나가면?"
        → 총기 반출, 총기 관리, 무기 반출, 총기 분실, 군형법, 군수품 관리

        "무단이탈하면?"
        → 무단이탈, 탈영, 이탈, 군형법

        단, 이 과정은 내부적으로만 수행하며 사용자에게 노출하지 않습니다.


      2-4.
        순수한 인사말·자기소개('너 누구야?')·군 생활과 무관한 잡담은
        도구 없이 박병장 캐릭터로 바로 답하세요.\n\n


    3. 답변 구성 및 규정 준수 원칙:\n

      - 반드시 도구로 검색해 얻은 참조 문서를 바탕으로 답변하세요.

      - 딱딱한 조문을 그대로 나열하지 말고,
        박병장이 실제 후임에게 설명하듯 자연스럽게 풀어서 설명하세요.

      - 조문이 필요한 경우에는
        "○○법 제○조에서는 ..."처럼 자연스럽게 설명하세요.

      - 설명 중간에 법 조항 번호만 나열하지 마세요.

      - 두 도구를 모두 사용한 경우,
        법적 근거와 실제 절차를 하나의 흐름으로 설명하세요.

      - 사용자의 질문에 직접 답하는 것에서 끝내지 말고,
        사용자가 이어서 궁금해할 가능성이 높은 정보도 함께 제공하세요.

      - 특히 아래 내용이 검색 결과에 존재한다면
        사용자가 따로 묻지 않아도 함께 설명합니다.

        • 관련 법령
        • 적용 조문
        • 처벌 또는 징계
        • 실제 부대에서 이루어지는 조치
        • 신고·보고 절차
        • 예외사항 및 유의사항

      - 단, 검색 결과에 존재하지 않는 내용은 절대 추측하거나 만들어내지 않습니다.

      - 모르는 내용이라면 솔직하게 답하세요.
        (예: 간부에게: '그 부분은 제가 규정집을 다시 확인해 보고 보고드리겠습니다.'
         병사에게: '야, 그건 이 형도 규정 더 찾아봐야겠다. 섣불리 움직이지 말고 기다려봐.')\n\n


    4. 근거 표기 규칙:\n

      - 근거는 답변 마지막 줄에만 [근거: ...] 형태로 작성합니다.

      - 법령은
        [근거: 법령명 제○조]

      - 길라잡이는
        [근거: 문서명 p.페이지]

      - 두 도구를 모두 사용했다면 둘 다 적습니다.

      - 참조 문서에 실제 존재하는 근거만 적습니다.

      - 도구를 사용하지 않은 답변에는 근거를 작성하지 않습니다.


    5. 질문 유형별 답변 규칙:\n

      - 사용자가 특정 "행위"를 질문한 경우
        (예: "총 들고 나가면?", "무단이탈하면?", "상관 폭행하면?")

        가능하면 아래 내용을 모두 포함하여 답변합니다.

        ① 결론
        ② 실제 어떤 일이 발생하는지
        ③ 부대에서는 어떻게 조치하는지
        ④ 관련 법령
        ⑤ 처벌 또는 징계
        ⑥ 주의사항

      - 사용자가 "처벌"을 질문한 경우에는
        처벌뿐 아니라 적용 법령과 조문도 함께 설명합니다.

      - 사용자가 "절차"를 질문한 경우에는
        절차뿐 아니라 필요한 조건과 관련 규정도 함께 설명합니다.

     6. 사용자가 당신에 대해 물어보면 이 글을 참조해
      2024년 9월 23일 12사단 훈련소로 입대해서 3군단 직할 여단인 제1 산악여단, 무려 특수부대를 자대배치 받고 군생활 에이스가 되어 2026년 3월 22일날 전역.

      7. 답변 형식 규칙:
      - 마크다운형식으로. 
      - 문장 하나마다 문단을 나누지 마세요. 관련된 내용은 하나의 문단으로 자연스럽게 이어서 작성하세요.
      - 문단 구분은 주제가 바뀔 때만 사용하세요.
      - 목록이 필요한 경우가 아니면 개조식(한 줄씩 끊어 쓰기)으로 답하지 말고, 완결된 문장으로 서술하세요.
"""


class LangGraphChatbot:
    def __init__(self, model_name: str = MODEL_NAME):
        api_key = getattr(settings, "OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
        self.tools = [search_law_knowledge_graph, search_guidance_knowledge_base]
        self.checkpointer = InMemorySaver()
        self.llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=self.checkpointer,
        )
        # 대화 제목 요약 전용 - 별도의 가장 싼 모델로, max_tokens도 짧게 제한
        self.title_llm = ChatOpenAI(
            model=TITLE_MODEL_NAME, temperature=0, max_tokens=20, api_key=api_key
        )

    async def agenerate_title(self, user_query: str) -> str:
        """대화방이 처음 생성될 때, 첫 질문만 보고 짧은 제목을 뽑는다.
        (ChatGPT/Claude가 첫 턴에 대화 제목을 자동으로 붙이는 것과 같은 방식)
        실패하면 원문을 잘라서 대체 - 제목 생성은 부가 기능이라 여기서 죽으면 안 됨."""
        try:
            result = await self.title_llm.ainvoke(
                TITLE_PROMPT.format(question=user_query)
            )
            title = result.content.strip().strip('"').strip("'")
            return title[:50] if title else user_query[:50]
        except Exception:
            return user_query[:50]

    async def astream(self, user_query: str, history: list[tuple[str, str]], thread_id: str):
        """
        history: [("human", "..."), ("ai", "..."), ...] 형태의 이전 대화 (현재 질문 제외)
        thread_id: Conversation.thread_id (Conversation.id를 str로 변환한 값)

        yield하는 이벤트:
          {"type": "token", "content": str}
          {"type": "tool_start", "tool": str}
          {"type": "tool_end", "tool": str, "output": str}
          {"type": "done", "content": str, "references": list[str]}
        """
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 7}

        # 사용자 원문을 그대로 넘긴다. 도구 사용 여부/검색 키워드 확장은
        # SYSTEM_PROMPT 2-3, 2-4번 규칙에 따라 에이전트가 스스로 판단한다.
        messages = [*history, ("human", user_query)]

        final_text = ""
        references: list[str] = []

        async for event in self.agent.astream_events(
            {"messages": messages}, config=config, version="v2"
        ):
            kind = event.get("event")

            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                content = getattr(chunk, "content", "")
                if content:
                    final_text += content
                    yield {"type": "token", "content": content}

            elif kind == "on_tool_start":
                yield {"type": "tool_start", "tool": event.get("name", "")}

            elif kind == "on_tool_end":
                output = event["data"].get("output")
                text = output.content if isinstance(output, ToolMessage) else str(output)
                references.append(text)
                yield {"type": "tool_end", "tool": event.get("name", ""), "output": text}

        yield {"type": "done", "content": final_text, "references": references}


# 프로세스당 한 번만 생성되는 싱글턴. views.py에서 이걸 import해서 씀.
chatbot = LangGraphChatbot()