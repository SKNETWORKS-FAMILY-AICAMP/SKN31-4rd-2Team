# 프로젝트 설정 및 실행 메모

## 1. 프로젝트 구조
- 루트 폴더: military_life
- 주요 앱:
  - account: 계정/로그인/프로필
  - board: 게시판 기능
  - chatbot: 챗봇 기능
  - home: 홈 화면
  - records: 기록/목표/일지
  - back_logic: 챗봇/검색/벡터 DB 로직
- 공통 디렉터리:
  - config: Django 설정/URL/WSGI/ASGI
  - static: 공통 정적 파일
  - templates: 공통 템플릿

## 2. 가상 환경 설정
- Python 3.13 가상 환경 생성 명령:
  - uv venv .venv --python 3.13
- 활성화 명령(Windows PowerShell):
  - .\.venv\Scripts\Activate.ps1
- 활성화 확인 방법:
  - $env:VIRTUAL_ENV
  - python --version
  - Get-Command python

## 3. 패키지 설치
- ipykernel 설치:
  - uv pip install ipykernel
- 설치 결과: ipykernel이 가상 환경에 정상 설치됨

## 4. 실행 관련 안내
- 팀원이 전달한 실행 순서:
  1. python manage.py makemigrations
  2. python manage.py migrate
  3. python board/create_dummy_data.py
  4. python manage.py runserver

## 5. 참고
- 현재 터미널은 PowerShell로 확인되었고, 가상 환경도 활성화되어 있음
- 가상 환경이 활성화되어 있어도 PowerShell 프롬프트에 표시가 안 보일 수 있음
