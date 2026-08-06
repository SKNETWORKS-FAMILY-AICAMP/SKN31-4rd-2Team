# CLAUDE.md

> 이 파일은 Claude Code가 세션 시작 시 자동으로 읽는 프로젝트 지침 파일입니다.
> 코딩을 공부하는 초급 개발자용 표준 템플릿이며, 프로젝트 루트(예: manage.py가 있는 위치)에
> `CLAUDE.md`라는 이름으로 저장하면 적용됩니다.
> 실제 프로젝트에 맞게 [ ] 표시된 부분을 채워서 사용하세요.

---

## 1. 프로젝트 개요

- 프로젝트명: military_life
- 목적: 군 생활 중 궁금한 점을 질문하면 관련 법률 및 규정을 찾아 쉽게 답변해주는 서비스
- 기술 스택: Python, Django 6.0, MySQL(mysqlclient), Qdrant, neo4j, LangChain, LangGraph, OpenAI API
- 개발 환경: Windows / VS Code / venv 가상환경(.venv) / Jupyter

---

## 2. 실행 방법 (자주 쓰는 명령어)

```bash
# 가상환경 활성화 (PowerShell, 프로젝트 루트에서)
.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-test.txt  # 테스트용 의존성(pytest 등)

# manage.py는 military_life/ 폴더 안에 있으므로 먼저 이동
cd military_life

# 개발 서버 실행
python manage.py runserver

# 마이그레이션
python manage.py makemigrations
python manage.py migrate

# 테스트 실행
python manage.py test
# 또는 pytest 사용 시
pytest
```

---

## 3. 코딩 컨벤션

- 변수/함수/파일명: snake_case, 클래스명: PascalCase, 상수명: UPPER_SNAKE_CASE
- 커밋 전 반드시 `ruff check . && ruff format .` 실행
- 함수 하나에 책임 하나만 (한 함수는 가급적 50줄 이내로 분리)
- 매직 넘버/문자열은 상수로 분리
- 공개 함수/클래스에는 Google 스타일 docstring 작성
- 주석은 "왜(why)"를 설명하고, "무엇(what)"은 코드 자체로 드러나게 작성
- 함수 시그니처에는 타입 힌트를 명시

---

## 4. 프로젝트 구조

```
SKN31-4th-2Team/
├── .env                    # 민감 정보(API 키 등), git에는 커밋하지 않음
├── requirements.txt        # 운영 의존성
├── requirements-test.txt   # 테스트 의존성 (pytest, pytest-django, pytest-playwright)
├── docs/
│   └── study-log/          # 코드 수정 기록 (7번 규칙 참고)
└── military_life/          # manage.py가 있는 Django 프로젝트 루트
    ├── manage.py
    ├── config/              # settings, urls, wsgi/asgi
    ├── account/             # 회원가입/로그인/회원정보 관리
    ├── board/               # 게시판
    ├── chatbot/             # 법률/규정 질의응답 챗봇
    ├── records/             # 개인 기록 관리
    ├── back_logic/          # 챗봇/검색 등 백엔드 로직 (RAG, LangChain 연동 등)
    ├── home/                # 메인/홈 화면
    ├── static/
    └── templates/
```

---

## 5. 절대 하지 말아야 할 것 (Guardrails)

- `.env`, API 키, 비밀번호 등 민감 정보를 코드에 하드코딩하지 않는다
- `git push --force`를 main/master 브랜치에 사용하지 않는다
- 프로덕션 DB에 직접 마이그레이션/쿼리를 실행하지 않는다
- `rm -rf`, `DROP TABLE` 등 파괴적 명령은 반드시 사용자에게 먼저 확인받는다
- 테스트 없이 핵심 로직을 임의로 수정하지 않는다

---

## 6. Claude에게 기대하는 협업 방식 (학습 관점)

- 코드를 대신 완성해주기보다, **단계별로 설명하며 함께 진행**할 것
- 에러 발생 시 원인을 먼저 설명하고, 해결책은 그 다음에 제시할 것
- 이해하지 못한 개념(예: WSGI, 가상환경, ORM 등)이 나오면 간단한 비유를 곁들여 설명할 것
- 불필요하게 복잡한 라이브러리/패턴 도입을 지양하고, 기본기에 집중할 것

---

## 7. 코드 수정 기록 규칙 (학습을 위한 필수 규칙)

> 코딩 실력 향상을 위해, 코드에 대한 모든 수정/구현 지시에는
> 수정 전·후 코드를 비교하며 공부할 수 있는 기록물을 남깁니다.

- Claude는 코드를 작성하거나 수정하는 모든 작업에 대해,
  작업 완료 후 `docs/study-log/[YYYY-MM-DD]-[간단한-제목].md` 파일을 생성한다.
- 기록물에는 아래 항목을 반드시 포함한다.
  - 지시 내용 (사용자가 요청한 작업 요약)
  - 수정 전 코드 (해당 파일/함수의 원래 상태, 신규 작성 시 "없음"으로 표기)
  - 수정 후 코드 (실제로 적용된 코드)
  - 변경 이유 및 핵심 개념 설명 (왜 이렇게 바꾸었는지, 관련 개념은 무엇인지)
- 파일이 여러 개 수정된 경우, 파일별로 수정 전/후를 구분하여 기록한다.
- 단순 오탈자 수정 등 학습 가치가 낮은 변경은 기록을 생략할 수 있다.
- 기록 파일명 예시: `docs/study-log/2026-08-05-로그인기능구현.md`

### 기록물 템플릿

```markdown
# [작업 제목]

## 지시 내용
[사용자가 요청한 내용 요약]

## 수정 전
\`\`\`python
[원래 코드 또는 "없음"]
\`\`\`

## 수정 후
\`\`\`python
[수정된 코드]
\`\`\`

## 변경 이유 및 개념 설명
[왜 이렇게 수정했는지, 관련된 개념 설명]
```

---

## 8. 참고 문서 링크

- 요구사항명세서: `docs/prd/요구사항_정의서.md`
- 테스트 계획: `docs/testing/login-toast-test-plan.md`
- 코드 수정 기록: `docs/study-log/` (7번 규칙에 따라 누적)
- PRD / API 명세: 아직 없음 — 작성되면 이 섹션에 경로 추가
