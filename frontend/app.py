import os
from typing import Any

import requests
import streamlit as st

DEFAULT_API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = 120

st.set_page_config(page_title="AI Data Agent", page_icon="🤖", layout="wide")


def ensure_session_state() -> None:
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = DEFAULT_API_BASE_URL
    if "sql_messages" not in st.session_state:
        st.session_state.sql_messages = []
    if "load_messages" not in st.session_state:
        st.session_state.load_messages = []
    if "last_uploaded_path" not in st.session_state:
        st.session_state.last_uploaded_path = ""

# 1. call_chat_api 함수 수정 (file_path 매개변수 추가)
def call_chat_api(endpoint: str, query: str, file_path: str = None) -> str:
    url = f"{st.session_state.api_base_url}{endpoint}"
    payload = {"query": query}
    if file_path:
        payload["file_path"] = file_path # 백엔드로 경로 함께 전송
        
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload_data: dict[str, Any] = response.json()
    return str(payload_data.get("answer", "No answer returned."))


def call_upload_api(uploaded_file) -> dict[str, Any]:
    url = f"{st.session_state.api_base_url}/upload"
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "text/csv",
        )
    }
    response = requests.post(url, files=files, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def check_backend_health() -> tuple[bool, str]:
    url = f"{st.session_state.api_base_url}/docs"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        return False, str(exc)
    return True, "Backend is reachable."


# 2. render_chat_tab 함수 수정 (call_chat_api 호출 부분)
def render_chat_tab(title: str, endpoint: str, state_key: str, input_key: str) -> None:
    st.subheader(title)

    for message in st.session_state[state_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Type your message", key=input_key)
    if not user_input:
        return

    st.session_state[state_key].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                # Load Agent 탭일 경우, 방금 업로드한 파일 경로를 가져옴
                current_file_path = None
                if endpoint == "/chat/load":
                    current_file_path = st.session_state.get("last_uploaded_path", "")
                
                # 수정된 API 호출 (경로를 함께 넘김)
                answer = call_chat_api(endpoint, user_input, current_file_path)
            except requests.RequestException as exc:
                answer = f"Request failed: {exc}"
            st.markdown(answer)

    st.session_state[state_key].append({"role": "assistant", "content": answer})
    
def render_upload_tab() -> None:
    st.subheader("CSV Upload")
    st.caption("Uploaded files are saved in backend data/uploads.")

    uploaded_file = st.file_uploader("Select CSV file", type=["csv"])
    if st.button("Upload", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.warning("Please select a CSV file first.")
            return

        with st.spinner("Uploading..."):
            try:
                result = call_upload_api(uploaded_file)
            except requests.RequestException as exc:
                st.error(f"Upload failed: {exc}")
                return

        file_path = str(result.get("path", ""))
        st.session_state.last_uploaded_path = file_path
        st.success(str(result.get("info", "Upload complete")))
        if file_path:
            st.code(file_path)

    if st.session_state.last_uploaded_path:
        st.info(
            "You can now ask the load agent like this:\n"
            f"- Load data from '{st.session_state.last_uploaded_path}' into the target table"
        )


ensure_session_state()

with st.sidebar:
    st.header("Connection")
    st.text_input("FastAPI URL", key="api_base_url")
    st.caption("Example: http://localhost:8000")

    if st.button("Check backend connection", use_container_width=True):
        ok, message = check_backend_health()
        if ok:
            st.success(message)
        else:
            st.error(f"Connection failed: {message}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear SQL chat", use_container_width=True):
            st.session_state.sql_messages = []
    with col2:
        if st.button("Clear Load chat", use_container_width=True):
            st.session_state.load_messages = []

st.title("AI Data Agent")
st.caption("Streamlit frontend for SQL Q&A and CSV loading with FastAPI backend")

sql_tab, load_tab, upload_tab = st.tabs(["SQL Chat", "CSV Load Chat", "CSV Upload"])

with sql_tab:
    render_chat_tab(
        title="SQL Query Agent",
        endpoint="/chat/sql",
        state_key="sql_messages",
        input_key="sql_chat_input",
    )

with load_tab:
    render_chat_tab(
        title="CSV Load Agent",
        endpoint="/chat/load",
        state_key="load_messages",
        input_key="load_chat_input",
    )

with upload_tab:
    render_upload_tab()
