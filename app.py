import streamlit as st
from rag_engine import ask

# 頁面設定
st.set_page_config(
    page_title="刑法小幫手",
    page_icon="⚖️",
    layout="centered"
)

# 自訂CSS
st.markdown("""
<style>
    .main { max-width: 800px; }
    .stChatMessage { border-radius: 12px; }
    .source-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 12px;
        border-radius: 4px;
        margin: 8px 0;
    }
    .article-num {
        font-weight: bold;
        color: #1f77b4;
        font-size: 1.05em;
    }
    .disclaimer {
        font-size: 0.8em;
        color: #888;
        text-align: center;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 標題區
st.title("⚖️ 中華民國刑法小幫手")
st.caption("基於 RAG 技術，提供法條查詢、引用與白話解釋")
st.markdown('<p class="disclaimer">⚠️ 本系統僅供學習參考，不構成法律建議，實際法律問題請諮詢專業律師。</p>', unsafe_allow_html=True)
st.divider()

# 範例問題
st.markdown("**💡 範例問題：**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("殺人罪的刑罰？"):
        st.session_state.example_query = "殺人罪的刑罰是什麼？"
with col2:
    if st.button("搶劫和偷竊的差別？"):
        st.session_state.example_query = "搶劫和偷竊怎麼區分？"
with col3:
    if st.button("什麼是正當防衛？"):
        st.session_state.example_query = "什麼是正當防衛？"

# 對話歷史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg:
            with st.expander("📋 參考法條"):
                for a in msg["sources"]:
                    st.markdown(f'<div class="source-box"><span class="article-num">{a["article"]}</span><br>{a["content"]}</div>', unsafe_allow_html=True)

# 處理範例問題或使用者輸入
query = st.chat_input("請輸入您的法律問題，例如：竊盜罪的刑罰是什麼？")
if "example_query" in st.session_state:
    query = st.session_state.pop("example_query")

if query:
    # 顯示使用者問題
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 取得RAG回答
    with st.chat_message("assistant"):
        with st.spinner("查詢法條中..."):
            result = ask(query)

        st.markdown(result["answer"])

        with st.expander("📋 參考法條"):
            for a in result["sources"]:
                st.markdown(f'<div class="source-box"><span class="article-num">{a["article"]}</span><br>{a["content"]}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })