# AIagent

프로젝트 디렉터리 구조는 아래와 같습니다.

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
│   │   ├── __init__.py
│   │   ├── sqlagent.py          # SQL 질의 에이전트 클래스/함수
│   │   └── loadagent.py         # CSV 적재 에이전트 클래스/함수
│   └── utils/                   # 유틸리티 스크립트
│       ├── __init__.py
│       └── create_empty_db.py   # DB 초기화 스크립트
│
├── frontend/                    # Streamlit UI 로직
│   └── app.py                   # 채팅 및 파일 업로드 화면 구성
│
├── .env                         # 환경 변수 (OLLAMA_SERVER_IP 등)
├── requirements.txt             # Python 의존성 목록
├── Dockerfile                   # Docker 이미지 빌드 파일
└── docker-compose.yml           # Docker Compose 실행 파일
```
