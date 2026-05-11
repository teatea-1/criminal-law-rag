import streamlit as st
from rag_engine import ask

# 頁面設定
st.set_page_config(
    page_title="刑法小幫手",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ 中華民國刑法小幫手")
st.caption("基於 RAG 技術，提供法條查詢、引用與白話解釋")

# 對話歷史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 輸入框
if query := st.chat_input("請輸入您的法律問題，例如：竊盜罪的刑罰是什麼？"):

    # 顯示使用者問題
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 取得RAG回答
    with st.chat_message("assistant"):
        with st.spinner("查詢法條中..."):
            result = ask(query)

        st.markdown(result["answer"])

        # 顯示引用來源
        with st.expander("📋 參考法條"):
            for a in result["sources"]:
                st.markdown(f"**{a['article']}**")
                st.markdown(a["content"])
                st.divider()

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"]
    })