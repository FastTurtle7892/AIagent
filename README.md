AIagent/
│
├── data/                    # 🗄️ 데이터베이스 및 업로드 파일 관리
│   ├── Chinook.db           # 원본 SQLite DB
│   ├── empty_chinook.db     # 비어있는 적재용 DB
│   ├── Album.csv            # 테스트용 샘플 CSV
│   └── uploads/             # (자동생성) 프론트엔드에서 업로드한 CSV 임시 저장소
│
├── backend/                 # ⚙️ FastAPI & LangChain 코어 로직
│   ├── main.py              # FastAPI 서버 엔드포인트 및 FastMCP 도구 정의
│   ├── agents/              # AI 에이전트 두뇌
│   │   ├── __init__.py
│   │   ├── sqlagent.py      # SQL 질의 에이전트 클래스/함수
│   │   └── loadagent.py     # CSV 적재 에이전트 클래스/함수
│   └── utils/               # 잡다한 유틸리티 스크립트
│       ├── __init__.py
│       └── create_empty_db.py # DB 초기화 스크립트
│
├── frontend/                # 🖥️ Streamlit UI 로직
│   └── app.py               # 채팅 및 파일 업로드 화면 구성
│
├── .env                     # 🔐 환경 변수 (OLLAMA_SERVER_IP 등 보관, 절대 Git에 안 올림)
├── requirements.txt         # 📦 패키지 의존성 목록
│
├── Dockerfile               # 🐳 도커 빌드 파일 (나중을 위해 루트에 보관)
└── docker-compose.yml       # 🐳 도커 컴포즈 파일 (나중을 위해 루트에 보관)