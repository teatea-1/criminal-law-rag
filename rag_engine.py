import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

# 載入環境變數
load_dotenv()
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 載入模型與資料庫
print("載入Embedding模型中...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
client_chroma = chromadb.PersistentClient(path="./chroma_db")
collection = client_chroma.get_collection("criminal_law")
print("載入完成！")

def search_articles(query: str, top_k: int = 5):
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

def ask(query: str):
    """RAG問答主函式"""
    # 1. 搜尋相關法條
    related_articles = search_articles(query)

    # 2. 組合成context
    context = "\n\n".join([
        f"{a['article']}：{a['content']}"
        for a in related_articles
    ])

    # 3. 建立prompt
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

    # 4. 呼叫Groq
    response = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": related_articles
    }


# 測試
if __name__ == "__main__":
    result = ask("殺人罪的刑罰是什麼？")
    print("=== 回答 ===")
    print(result["answer"])
    print("\n=== 引用法條 ===")
    for a in result["sources"]:
        print(f"- {a['article']}")