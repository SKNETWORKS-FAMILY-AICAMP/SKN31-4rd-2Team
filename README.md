# SKN31-4rd-2Team

## 📑 목차
 
- [👥 팀 소개](#-팀-소개)
- [📖 프로젝트 개요](#-프로젝트-개요)
- [🔄 주요 기능](#-주요-기능)
- [🛠 기술 스택](#-기술-스택)
- [📁 프로젝트 구조](#-프로젝트-구조)
- [🏗 시스템 아키텍처](#-시스템-아키텍처)
- [🌐 배포 정보](#-배포-정보)
- [📸 화면 설계](#-화면-설계)
- [📄 프로젝트 산출물](#-프로젝트-산출물)
- [💬 한줄 회고](#-한줄-회고)

---

## 1. 팀명 및 팀원 소개
## 🪖 진격의 박병장

| 전서연 | 고현아 | 김세희 | 이용혁 | 박동관 |
| :---: | :---: | :---: | :---: | :---: |
| <a href="https://github.com/sxoxyn"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> | <a href="https://github.com/hellene0708-cyber"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> | <a href="https://github.com/kimsehuikim"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> | <a href="https://github.com/leeyonghyok"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> |  <a href="https://github.com/Parkdongkwan"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> |
|<img src="military_life/images/sy.png" width="150" height="150"> | <img src="military_life/images/ha.png" width="150" height="150"> | <img src="military_life/images/sh.png" width="150" height="150"> | <img src="military_life/images/yh.png" width="150" height="150"> | <img src="military_life/images/dg.png" width="150" height="150"> |
| <b>PM/FE</b>     |<b>FE</b>  |<b>FE</b>   |<b>FE</b>  | <b>BE</b>   | | 

---

## 1-1. WBS

각자 본인이 담당한 부분 작성해서 저(김세희)한테 보내주세요

---

## 2. 프로젝트 개요

### 2-1. 프로젝트 소개
진격의 박병장은 군 장병에게 필요한 정보를 쉽고 빠르게 제공하기 위한 **LLM 기반 군 생활 지원 웹 애플리케이션**입니다.

군 관련 AI 챗봇과 회원 관리, 개인 기록, 익명 게시판 기능을 제공하며, Django와 AWS를 활용해 실제 서비스 형태로 구현했습니다.

### 2-2. 주제 선정 이유 및 목표

3차 프로젝트에서는 군 관련 법령과 병영생활 정보를 제공하는 RAG 기반 AI 챗봇을 개발했습니다.

4차 프로젝트에서는 사용자의 지속적인 서비스 활용을 위해 기존 AI 챗봇을 중심으로 다음 기능을 추가하고, Django 기반 웹 애플리케이션으로 확장했습니다.

- 회원 관리
- 개인 기록 (D-day · 캘린더 · 목표)
- 익명 게시판

또한 AWS에 배포하여 실제 사용 가능한 군 생활 지원 서비스를 구축하는 것을 목표로 프로젝트를 진행했습니다.
  

---

## 3. 주요 기능

3차 프로젝트에서는 **LLM 기반 RAG 챗봇** 구현에 초점을 맞췄다면,
4차 프로젝트에서는 기존 챗봇을 기반으로 실제 사용 가능한 **군 생활 통합 웹 애플리케이션**으로 확장했습니다.

> 

| 기능 | 설명 |
|---|---|
| 🏠 **Home** | 서비스 소개 · 전역 D-day · 주요 기능 바로가기 |
| 👤 **User** | 회원가입 · 로그인 · 계급 기반 맞춤 서비스 |
| 🤖 **AI Chatbot** | 실시간 스트리밍 · 대화 저장 · 이전 대화 관리 |
| 📝 **Record** | 전역 D-day · 캘린더 · 목표 관리 |
| 👥 **Community** | 익명 게시판 · 댓글 · 좋아요 · 검색 |
| ☁️ **Deployment** | Django 기반 웹 서비스 · AWS EC2 · AWS RDS |

---

## 4. 기술 스택

| Layer | Technology |
|------|------------|
| **Language** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) |
| **Backend** | ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) |
| **AI / RAG** | ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat) ![LangGraph](https://img.shields.io/badge/LangGraph-000000?style=flat) |
| **Database** | ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white) ![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?style=flat&logo=neo4j&logoColor=white) ![Qdrant](https://img.shields.io/badge/Qdrant-EF3A5D?style=flat) |
| **Infrastructure** | ![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=flat&logo=amazonaws&logoColor=white) ![AWS RDS](https://img.shields.io/badge/AWS_RDS-527FFF?style=flat&logo=amazonaws&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat) |

---

## 5. 프로젝트 구조 

```text
SKN31-4th-2Team
├── military_life
│   ├── account/              # 회원가입, 로그인 및 사용자 관리
│   ├── back_logic/           # RAG 검색 및 AI 챗봇 로직
│   │   ├── chatbot.py
│   │   ├── graphdb_retriever.py
│   │   ├── vectordb_retriever.py
│   │   └── tools.py
│   │
│   ├── board/               # 익명 게시판 기능
│   ├── chatbot/             # 챗봇 앱
│   │   ├── migrations/
│   │   ├── static/
│   │   ├── templates/
│   │   ├── admin.pys
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── config/              # Django 프로젝트 설정
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── home/                # 메인(Home) 페이지
│   ├── records/             # 개인 기록(D-day, 캘린더, 목표)
│   ├── static/              # CSS, JavaScript, 이미지, 폰트
│   ├── templates/           # 공통 HTML 템플릿
│   ├── images/              # README 이미지
│   ├── manage.py
│   ├── requirements-linux.txt
│   └── deploy.sh
│
├── README.md
├── requirements-linux.txt
└── requirements-test.txt
```
---

## 6. 시스템 아키텍처

---

## 7. 배포 정보
### AWS EC2 URL

| 구분 | URL |
|------|-----|
| 🏠 서비스 | http://43.200.132.171
| 🔑 Admin | http://43.200.132.171/admin |

> **배포 환경:** AWS EC2 (Ubuntu 24.04 LTS) + AWS RDS(MySQL)

## 8. 화면 설계
### 8-1. 홈화면
서비스 소개, 전역 D-Day, 복무 진행률과 주요 기능 바로가기를 한눈에 확인하는 메인 화면
<img src="military_life/images/홈화면.png">

### 8-2. 로그인
아이디와 비밀번호를 입력해 로그인하고, 회원가입 탭으로 전환할 수 있는 화면
<img src="military_life/images/로그인.png">

### 8-3. 회원가입
아이디·이메일·비밀번호와 입대일, 신분(병사/간부)·계급을 입력해 계정을 생성하는 화면
<img src="military_life/images/회원가입.png">

### 8-4-1. 개인기록: D-day
전역까지 남은 일수(D-Day)와 전역 예정일, 복무 진행률·통계를 확인하는 화면
<img src="military_life/images/개인기록_Dday.png">

### 8-4-2. 개인기록: 캘린더
월별 캘린더에서 휴가·외박 등 일정을 등록하고 조회하는 화면
<img src="military_life/images/개인기록_캘린더.png">

### 8-4-3. 개인기록: 목표
카테고리별 목표를 추가하고 달성률·목표일을 관리하는 화면
<img src="military_life/images/개인기록_목표.png">

### 8-5-1. 커뮤니티: 게시판
카테고리별 게시글을 검색·열람하고 새 글을 작성할 수 있는 익명 게시판 목록 화면
<img src="military_life/images/커뮤니티_게시판.png">

### 8-5-2. 커뮤니티: 게시글
게시글 본문과 댓글을 확인하고 좋아요·댓글 작성·신고가 가능한 게시글 상세 화면
<img src="military_life/images/커뮤니티_게시글.png">

### 8-6. 회원 정보 수정
아이디·비밀번호·신분·계급 등 회원 정보를 수정하거나 탈퇴할 수 있는 화면
<img src="military_life/images/회원정보수정.png">

### 8-7. 내가 쓴 게시글
본인이 작성한 게시글 목록을 확인하고 삭제할 수 있는 화면
<img src="military_life/images/내가_쓴_게시글.png">

---

## 9. 프로젝트 산출물

프로젝트 진행 과정에서 작성한 주요 산출물입니다.

| 산출물 | 자세히 보기 |
|--------|------|
| 📋 **요구사항 정의서** | [⌜요구사항 정의서⌟](산출물/요구사항_정의서.md) |
| 🧮 **테이블 정의서** | [⌜테이블 정의서⌟](산출물/테이블_정의서.md) |
| 🎨 **화면 설계서** | [⌜화면 설계서](산출물/화면_설계서.md) |
| 🏗 **시스템 구성도** | [⌜시스템 구성도⌟](산출물/시스템_구성도.md) |
| 🧪 **테스트 계획서 및 테스트 결과 보고서** | [⌜테스트 계획서⌟](산출물/.md) , [⌜테스트 결과 보고서⌟](산출물/.md) |

---

## 10. 한줄 회고
전서연

고현아

김세희

박동관

이용혁




                    ┌───────────────────────┐
                    │       사용자(User)    │
                    └───────────┬───────────┘
                                │
                               HTTP
                                │
                                ▼
                  ┌────────────────────────┐
                  │     AWS EC2 (Ubuntu)   │
                  │────────────────────────│
                  │        Nginx           │
                  │            │           │
                  │        Gunicorn        │
                  │            │           │
                  │     Django Web Server  │
                  └───────────┬────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌────────────┐ ┌────────────┐ ┌──────────────┐
        │ AI Chatbot │ │ Community  │ │ Personal     │
        │  Service   │ │   Board    │ │   Records    │
        └─────┬──────┘ └─────┬──────┘ └──────┬───────┘
              │              │               │
              └──────────────┴───────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │    MySQL (AWS RDS)      │
                  │ 회원·게시글·대화·기록 저장 │
                  └─────────────────────────┘

        AI Chatbot Service
              │
              ▼
      ┌───────────────────────┐
      │    LangGraph Agent    │
      └───────────┬───────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 ┌──────────────┐    ┌──────────────┐
 │    Neo4j     │    │   Qdrant     │
 │ 군 법령 검색  │    │ 병영생활 검색 │
 └──────────────┘    └──────────────┘
        │                   │
        └─────────┬─────────┘
                  ▼
             OpenAI LLM
                  │
                  ▼
              답변 반환
