import os
from pathlib import Path
from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_ollama import ChatOllama

# 절대 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHINOOK_DB_PATH = BASE_DIR / "data" / "Chinook.db"

def get_sql_agent():
    # LLM 설정
    SERVER_IP = os.getenv("OLLAMA_SERVER_IP", "172.30.1.44")
    model = ChatOllama(
        model="qwen3:8b",
        base_url=f"http://{SERVER_IP}:11434",
        temperature=0,
        keep_alive="0", 
    )
    
    # DB 및 툴킷 설정
    db = SQLDatabase.from_uri(f"sqlite:///{CHINOOK_DB_PATH}")
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    
    system_prompt = """
    당신은 SQL 데이터베이스와 상호작용하도록 설계된 에이전트입니다.
    쿼리 결과가 최대 5개를 넘지 않도록 제한해야 하며, 특정 테이블의 모든 열(*)을 한 번에 조회하지 마세요.
    데이터베이스에 어떠한 DML 구문(INSERT, UPDATE, DELETE 등)도 실행해서는 안 됩니다.
    모든 작업이 끝나고 사용자에게 최종 정답을 반환할 때는 반드시 자연스러운 한국어로 답변하세요.
    """
    
    return create_agent(model, toolkit.get_tools(), system_prompt=system_prompt)