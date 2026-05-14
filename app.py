import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
import json

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

@st.cache_resource
def init_system():
    """初始化向量資料庫與模型（只執行一次）"""
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    client_chroma = chromadb.PersistentClient(path="./chroma_db")

    # 檢查collection是否已存在
    existing = [c.name for c in client_chroma.list_collections()]

    if "criminal_law" not in existing:
        st.info("🔄 第一次啟動，正在建立向量資料庫（約需1～2分鐘）...")

        with open("criminal_law.json", "r", encoding="utf-8") as f:
            articles = json.load(f)

        collection = client_chroma.create_collection("criminal_law")

        texts = [a["full_text"] for a in articles]
        ids = [a["article"] for a in articles]
        metadatas = [{"article": a["article"], "content": a["content"]} for a in articles]

        batch_size = 50
        for i in range(0, len(texts), batch_size):
            embeddings = model.encode(texts[i:i+batch_size]).tolist()
            collection.add(
                documents=texts[i:i+batch_size],
                embeddings=embeddings,
                ids=ids[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )
    else:
        collection = client_chroma.get_collection("criminal_law")

    return model, collection

def search_articles(model, collection, query: str, top_k: int = 5):
    """搜尋最相關的法條"""
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    articles = []
    for i in range(len(results["ids"][0])):
        articles.append({
            "article": results["metadatas"][0][i]["article"],
            "content": results["metadatas"][0][i]["content"],
        })
    return articles

def ask(model, collection, query: str):
    """RAG問答主函式"""
    from groq import Groq
    client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

    related_articles = search_articles(model, collection, query)
    context = "\n\n".join([f"{a['article']}：{a['content']}" for a in related_articles])

    prompt = f"""你是一位專業的中華民國刑法助理，請根據以下法條回答問題。

回答格式要求：
1. 【法條引用】：列出相關法條條號與原文
2. 【法律解釋】：用白話說明法條的意思
3. 【回答問題】：針對使用者的問題給出具體回答

注意：只能根據提供的法條內容回答，若法條中沒有相關資訊請如實告知。

相關法條：
{context}

使用者問題：{query}
"""
    response = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "answer": response.choices[0].message.content,
        "sources": related_articles
    }

# 初始化系統
model, collection = init_system()

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

# 處理輸入
query = st.chat_input("請輸入您的法律問題，例如：竊盜罪的刑罰是什麼？")
if "example_query" in st.session_state:
    query = st.session_state.pop("example_query")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("查詢法條中..."):
            result = ask(model, collection, query)
        st.markdown(result["answer"])
        with st.expander("📋 參考法條"):
            for a in result["sources"]:
                st.markdown(f'<div class="source-box"><span class="article-num">{a["article"]}</span><br>{a["content"]}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })