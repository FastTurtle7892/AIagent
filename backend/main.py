import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastmcp import FastMCP

# ✨ 모듈화된 에이전트 가져오기
from backend.agents.sqlagent import get_sql_agent
from backend.agents.loadagent import get_load_agent, get_csv_headers, load_csv_to_db

# 업로드 폴더 설정
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="AI Data Agent API")

# FastMCP 서버 설정 (추후 외부 시스템과 도구 연동 시 사용)
mcp = FastMCP("DataAgentTools")

# ---------------------------------------------------------
# API 라우터 (엔드포인트)
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    query: str

@app.post("/chat/sql")
async def chat_sql(request: ChatRequest):
    # SQL 에이전트 생성 및 실행
    agent = get_sql_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": request.query}]})
    return {"answer": response["messages"][-1].content}

@app.post("/chat/load")
async def chat_load(request: ChatRequest):
    # Load 에이전트 생성 및 실행
    agent = get_load_agent()
    response = agent.invoke({"messages": [{"role": "user", "content": request.query}]})
    return {"answer": response["messages"][-1].content}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    # 파일 저장
    file_location = UPLOAD_DIR / file.filename
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
        
    return {
        "info": f"파일 '{file.filename}' 저장 완료", 
        "path": str(file_location)
    }