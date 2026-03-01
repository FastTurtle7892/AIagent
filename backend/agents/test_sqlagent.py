import os
from dotenv import load_dotenv
import pathlib
import requests
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from pathlib import Path

load_dotenv()

# ---------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------
load_dotenv() 

# os.getenv("변수명", "기본값") 형태로 사용합니다.
SERVER_IP = os.getenv("OLLAMA_SERVER_IP", "127.0.0.1") 
model = ChatOllama(
    model="qwen3:8b",
    base_url=f"http://{SERVER_IP}:11434",
    temperature=0,
)


# DB 연결
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "Chinook.db"
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

print(f"사용 가능한 테이블: {db.get_usable_table_names()}")

# 데이터베이스 상호작용을 위한 Tool(도구) 추가
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

# Agent 프롬프트 작성
system_prompt = """
당신은 SQL 데이터베이스와 상호작용하도록 설계된 에이전트입니다.

입력된 질문이 주어지면, 문법적으로 올바른 {dialect} 쿼리를 작성하여 실행한 뒤, 그 결과를 확인하고 최종 답변을 반환하세요.
사용자가 특정 개수의 결과를 원한다고 명시하지 않는 한, 항상 쿼리 결과가 최대 {top_k}개를 넘지 않도록 제한해야 합니다.

데이터베이스에서 가장 유의미한 예시를 반환할 수 있도록 적절한 열(column)을 기준으로 결과를 정렬할 수 있습니다.
절대 특정 테이블의 모든 열(*)을 한 번에 조회하지 마시고, 질문과 관련된 열만 명시하여 조회하세요.

쿼리를 실행하기 전에 반드시 쿼리에 오류가 없는지 다시 한번 확인(double check)해야 합니다.
만약 쿼리를 실행하다가 에러가 발생하면, 에러를 참고하여 쿼리를 수정한 뒤 다시 시도하세요.

데이터베이스에 어떠한 DML 구문(INSERT, UPDATE, DELETE, DROP 등)도 절대 실행해서는 안 됩니다.

작업을 시작할 때, 가장 먼저 데이터베이스에 어떤 테이블들이 있는지 확인하는 과정을 반드시 거치세요. 이 단계는 절대 건너뛰면 안 됩니다.
테이블 목록을 확인한 후에는, 질문과 가장 관련성이 높은 테이블들의 스키마(구조)를 조회하여 파악하세요.

모든 데이터 조회를 마치고 사용자에게 **최종 정답(Final Answer)을 반환할 때만 반드시 자연스러운 한국어로 번역하여 답변**하세요.


""".format(
    dialect=db.dialect,
    top_k=5,
)

# SQL Agent 생성 (최신 LangChain 문법 적용)
agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
)

# Agent 실행 및 테스트
question = "Which genre on average has the longest tracks? (평균적으로 가장 곡 길이가 긴 장르는 무엇인가요?)"
print(f"\n질문: {question}\n")

# 스트리밍 모드로 Agent의 사고 과정(Tool 호출 등)을 터미널에 출력
for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()