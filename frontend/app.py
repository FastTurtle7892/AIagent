import os
from typing import Any

import requests
import streamlit as st

DEFAULT_API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = 120


st.set_page_config(page_title="AI Data Agent", page_icon="📊", layout="wide")


def ensure_session_state() -> None:
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = DEFAULT_API_BASE_URL
    if "sql_messages" not in st.session_state:
        st.session_state.sql_messages = []
    if "load_messages" not in st.session_state:
        st.session_state.load_messages = []
    if "last_uploaded_path" not in st.session_state:
        st.session_state.last_uploaded_path = ""


def call_chat_api(endpoint: str, query: str) -> str:
    url = f"{st.session_state.api_base_url}{endpoint}"
    response = requests.post(url, json={"query": query}, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    return str(payload.get("answer", "응답이 비어 있습니다."))


def call_upload_api(uploaded_file) -> dict[str, Any]:
    url = f"{st.session_state.api_base_url}/upload"
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "text/csv")}
    response = requests.post(url, files=files, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def render_chat_tab(title: str, endpoint: str, state_key: str, input_key: str) -> None:
    st.subheader(title)

    for message in st.session_state[state_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("질문을 입력하세요", key=input_key)
    if not user_input:
        return

    st.session_state[state_key].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("응답 생성 중..."):
            try:
                answer = call_chat_api(endpoint, user_input)
            except requests.RequestException as exc:
                answer = f"요청 실패: {exc}"
            st.markdown(answer)

    st.session_state[state_key].append({"role": "assistant", "content": answer})


def render_upload_tab() -> None:
    st.subheader("CSV 업로드")
    st.caption("업로드한 파일은 백엔드의 data/uploads 디렉터리에 저장됩니다.")

    uploaded_file = st.file_uploader("CSV 파일 선택", type=["csv"])
    if st.button("업로드 실행", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.warning("먼저 CSV 파일을 선택하세요.")
            return

        with st.spinner("업로드 중..."):
            try:
                result = call_upload_api(uploaded_file)
            except requests.RequestException as exc:
                st.error(f"업로드 실패: {exc}")
                return

        file_path = str(result.get("path", ""))
        st.session_state.last_uploaded_path = file_path
        st.success(str(result.get("info", "업로드 완료")))
        if file_path:
            st.code(file_path)

    if st.session_state.last_uploaded_path:
        st.info(
            "적재 에이전트에 아래처럼 요청해보세요:\n"
            f"- '{st.session_state.last_uploaded_path}' 파일을 원하는 테이블에 적재해줘"
        )


ensure_session_state()

with st.sidebar:
    st.header("연결 설정")
    st.text_input("FastAPI URL", key="api_base_url")
    st.caption("예: http://localhost:8000")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("SQL 대화 초기화", use_container_width=True):
            st.session_state.sql_messages = []
    with col2:
        if st.button("적재 대화 초기화", use_container_width=True):
            st.session_state.load_messages = []

st.title("AI Data Agent")
st.caption("FastAPI 기반 SQL 질의/CSV 적재 에이전트와 연동되는 Streamlit 프론트엔드")

sql_tab, load_tab, upload_tab = st.tabs(["SQL 채팅", "CSV 적재 채팅", "CSV 업로드"])

with sql_tab:
    render_chat_tab(
        title="SQL 질의 에이전트",
        endpoint="/chat/sql",
        state_key="sql_messages",
        input_key="sql_chat_input",
    )

with load_tab:
    render_chat_tab(
        title="CSV 적재 에이전트",
        endpoint="/chat/load",
        state_key="load_messages",
        input_key="load_chat_input",
    )

with upload_tab:
    render_upload_tab()
