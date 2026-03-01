# AI Data Agent

FastAPI 기반의 백엔드와 Streamlit 기반의 프론트엔드로 구성된 AI 데이터 분석 에이전트 서비스입니다. 사용자는 CSV 파일을 업로드하고, AI 에이전트를 통해 SQL 질의 및 데이터 적재 작업을 대화형으로 수행할 수 있습니다.

## 📂 프로젝트 구조

```text
AIagent/
├── data/                        # 데이터베이스 및 업로드 파일 관리
│   ├── Chinook.db               # 원본 SQLite DB
│   ├── empty_chinook.db         # 비어 있는 적재용 DB
│   ├── Album.csv                # 테스트용 샘플 CSV
│   └── uploads/                 # (자동 생성) 프론트엔드 업로드 CSV 임시 저장소
│
├── backend/                     # FastAPI & LangChain 코어 로직
│   ├── main.py                  # FastAPI 서버 라우트 정의 및 FastMCP 연동
│   ├── agents/                  # AI 에이전트 모듈
│   │   ├── sqlagent.py          # SQL 질의 에이전트
│   │   └── loadagent.py         # CSV 적재 에이전트
│   └── utils/                   # DB 초기화 등의 유틸리티 스크립트
│
├── frontend/                    # Streamlit UI 로직
│   └── app.py                   # 채팅 및 파일 업로드 화면 구성
│
├── .env                         # 환경 변수 (OLLAMA_SERVER_IP 등)
├── requirements.txt             # Python 의존성 목록
├── Dockerfile                   # 백엔드용 Docker 이미지 빌드 파일
└── docker-compose.yml           # Docker Compose 실행 파일
```

## ✨ 주요 기능
1. **SQL Chat Agent**: 자연어로 데이터베이스에 질의할 수 있는 챗봇 기능 
2. **CSV Load Agent**: 업로드한 CSV 데이터를 DB에 적재하는 과정을 도와주는 기능
3. **CSV Upload**: 사용자 화면에서 CSV 파일을 백엔드 서버로 직접 업로드하는 기능

## 🚀 실행 방법
uvicorn backend.main:app --reload
streamlit run frontend/app.py