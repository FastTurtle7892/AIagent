import os
import pandas as pd
import sqlite3
from pathlib import Path
from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_ollama import ChatOllama
from langchain.tools import tool

# 절대 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EMPTY_DB_PATH = BASE_DIR / "data" / "empty_chinook.db"

# 🛠️ 커스텀 도구 정의
@tool
def get_csv_headers(csv_file_path: str) -> str:
    """CSV 파일의 경로를 입력받아 컬럼명 목록을 반환합니다."""
    try:
        df = pd.read_csv(csv_file_path, nrows=0)
        return f"'{csv_file_path}' 파일의 컬럼명: {list(df.columns)}"
    except Exception as e:
        return f"파일 읽기 실패: {str(e)}"

@tool
def load_csv_to_db(csv_file_path: str, table_name: str) -> str:
    """CSV 데이터를 SQLite 테이블에 삽입(INSERT)합니다."""
    try:
        df = pd.read_csv(csv_file_path)
        conn = sqlite3.connect(EMPTY_DB_PATH)
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()
        return f"성공: {len(df)}행의 데이터를 '{table_name}' 테이블에 적재했습니다."
    except Exception as e:
        return f"적재 실패: {str(e)}"

def get_load_agent():
    # LLM 설정
    SERVER_IP = os.getenv("OLLAMA_SERVER_IP", "172.30.1.44")
    model = ChatOllama(
        model="qwen3:8b",
        base_url=f"http://{SERVER_IP}:11434",
        temperature=0,
        keep_alive="0", 
    )
    
    # DB 및 툴킷 설정
    db = SQLDatabase.from_uri(f"sqlite:///{EMPTY_DB_PATH}")
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools() + [get_csv_headers, load_csv_to_db]
    
    system_prompt = """
    당신은 똑똑한 데이터베이스 관리자입니다.
    사용자가 특정 CSV 파일을 적재해 달라고 요청하면 다음 순서를 따르세요:
    1. 데이터베이스 파악 (테이블 및 스키마 조회)
    2. 'get_csv_headers' 도구로 CSV 구조 파악
    3. 구조를 비교하여 매칭되는 테이블 추론
    4. 'load_csv_to_db' 도구로 데이터 적재
    최종 결과는 반드시 자연스러운 한국어로 답변하세요.
    """
    
    return create_agent(model, tools, system_prompt=system_prompt)