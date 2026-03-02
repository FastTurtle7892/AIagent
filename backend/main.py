import os
import io
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastmcp import FastMCP
from typing import Optional

# ✨ 모듈화된 에이전트 및 메모리 저장소 가져오기
from backend.agents.sqlagent import get_sql_agent
from backend.agents.loadagent import get_load_agent, UPLOADED_CSV_DATA

app = FastAPI(title="AI Data Agent API")

# FastMCP 서버 설정 (추후 외부 시스템과 도구 연동 시 사용)
mcp = FastMCP("DataAgentTools")

# ---------------------------------------------------------
# API 라우터 (엔드포인트)
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    query: str
    file_id: Optional[str] = None  # 프론트엔드에서 넘겨줄 메모리 데이터 ID

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
    
    # 에이전트가 "방금 업로드한 데이터"를 이해할 수 있도록 문맥(Context) 주입
    query_with_context = request.query
    if request.file_id:
        query_with_context += f"\n\n[System Note: 사용자가 방금 입력한 데이터의 ID는 '{request.file_id}' 입니다. 이 데이터를 분석하거나 적재할 때 이 ID를 사용하세요.]"
        
    response = agent.invoke({"messages": [{"role": "user", "content": query_with_context}]})
    return {"answer": response["messages"][-1].content}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    # ✨ 파일을 디스크에 저장하지 않고, 즉시 바이트로 읽어 메모리(Pandas DataFrame)로 올립니다.
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    # 식별자로 파일명을 사용
    file_id = file.filename
    UPLOADED_CSV_DATA[file_id] = df
        
    return {
        "info": f"데이터 '{file.filename}' 입력 및 메모리 로드 완료", 
        "file_id": file_id
    }