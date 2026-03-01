import pandas as pd
import sqlite3
from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_ollama import ChatOllama
from langchain.tools import tool

# ---------------------------------------------------------
# 🛠️ 도구 1: CSV 컬럼명 확인 도구 (새로 추가된 '눈' 역할)
# ---------------------------------------------------------
@tool
def get_csv_headers(csv_file_path: str) -> str:
    """
    이 도구는 CSV 파일의 경로를 입력받아, 해당 파일의 첫 번째 줄(컬럼명 목록)을 반환합니다.
    어떤 테이블에 데이터를 넣어야 할지 결정하기 위해 CSV의 구조(스키마)를 파악할 때 반드시 먼저 사용하세요.
    """
    try:
        # nrows=0 옵션을 주면 데이터는 빼고 컬럼명만 아주 빠르게 읽어옵니다.
        df = pd.read_csv(csv_file_path, nrows=0)
        columns = list(df.columns)
        return f"'{csv_file_path}' 파일의 컬럼명: {columns}"
    except Exception as e:
        return f"파일 읽기 실패. 오류 내용: {str(e)}"

# ---------------------------------------------------------
# 🛠️ 도구 2: CSV 적재 도구 (기존과 동일)
# ---------------------------------------------------------
@tool
def load_csv_to_db(csv_file_path: str, table_name: str) -> str:
    """
    이 도구는 CSV 파일의 경로와 테이블 이름을 입력받아,
    데이터를 한 번에 삽입(INSERT)합니다.
    """
    try:
        df = pd.read_csv(csv_file_path)
        conn = sqlite3.connect("empty_chinook.db")
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()
        return f"성공! '{csv_file_path}' 파일에서 {len(df)}개의 행을 '{table_name}' 테이블에 완벽하게 적재했습니다."
    except Exception as e:
        return f"적재 실패. 오류 내용: {str(e)}"

# ---------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------
SERVER_IP = ""
model = ChatOllama(
    model="qwen3:8b",
    base_url=f"http://{SERVER_IP}:11434",
    temperature=0,
    keep_alive="0", 
)

db = SQLDatabase.from_uri("sqlite:///empty_chinook.db")

# ---------------------------------------------------------
# 무기 장착 (새로운 도구 포함!)
# ---------------------------------------------------------
toolkit = SQLDatabaseToolkit(db=db, llm=model)
sql_tools = toolkit.get_tools()
# 두 가지 커스텀 도구를 모두 AI에게 줍니다.
all_tools = sql_tools + [get_csv_headers, load_csv_to_db] 

# ---------------------------------------------------------
# Agent 프롬프트 작성 (작업 순서를 훨씬 더 똑똑하게 수정)
# ---------------------------------------------------------
system_prompt = """
당신은 똑똑한 데이터베이스 관리자(AI 에이전트)입니다.
사용자가 특정 CSV 파일을 데이터베이스에 적재해 달라고 요청하면, 당신이 스스로 알맞은 테이블을 찾아야 합니다.

[필수 작업 순서 - 반드시 이 순서대로 도구를 호출하세요]
1. 데이터베이스 파악: 먼저 DB에 어떤 테이블들이 있는지, 각 테이블의 스키마(컬럼명)는 무엇인지 조회하세요.
2. CSV 파일 파악: 'get_csv_headers' 도구를 사용하여 타겟 CSV 파일의 컬럼명(구조)이 무엇인지 읽어오세요.
3. 매칭 및 추론: CSV 파일의 컬럼명과 DB 테이블들의 컬럼명을 비교하여, 이 데이터가 어느 테이블에 들어가야 하는지 스스로 판단하세요.
4. 데이터 적재: 알맞은 테이블 이름을 찾아냈다면, 'load_csv_to_db' 도구를 호출하여 적재를 실행하세요.

[언어 지침]
추론하고 도구를 사용하는 과정의 포맷은 그대로 유지하되, 모든 작업이 끝나고 사용자에게 **최종 결과(Final Answer)를 반환할 때는 반드시 자연스러운 한국어로 답변**하세요. (예: "CSV 파일의 컬럼을 확인한 결과, OOO 테이블이 가장 적합하여 적재를 완료했습니다.")
""".format()

# Agent 생성
agent = create_agent(
    model,
    all_tools,
    system_prompt=system_prompt,
)

# ---------------------------------------------------------
# Agent 실행 및 테스트
# ---------------------------------------------------------
question = "C:\\Users\\user\\Desktop\\AI_AGENT\\Album.csv 파일 안에 있는 데이터를 empty_chinook.db 안의 알맞은 테이블에 알아서 매칭해서 적재해줄래?"
print(f"\n요청: {question}\n")

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()