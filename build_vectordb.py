import json
from sentence_transformers import SentenceTransformer
import chromadb

# 讀取法條JSON
with open("criminal_law.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

print(f"載入 {len(articles)} 條法條")

# 載入多語言Embedding模型（支援中文，免費）
print("載入Embedding模型中...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# 建立Chroma資料庫
client = chromadb.PersistentClient(path="./chroma_db")

# 如果collection已存在就刪除重建
try:
    client.delete_collection("criminal_law")
except:
    pass

collection = client.create_collection("criminal_law")

# 批次建立Embedding並存入Chroma
print("建立向量資料庫中（約需1～2分鐘）...")

texts = [a["full_text"] for a in articles]
ids = [a["article"] for a in articles]
metadatas = [{"article": a["article"], "content": a["content"]} for a in articles]

# 批次處理避免記憶體問題
batch_size = 50
for i in range(0, len(texts), batch_size):
    batch_texts = texts[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    batch_metadatas = metadatas[i:i+batch_size]

    embeddings = model.encode(batch_texts).tolist()

    collection.add(
        documents=batch_texts,
        embeddings=embeddings,
        ids=batch_ids,
        metadatas=batch_metadatas
    )
    print(f"進度：{min(i+batch_size, len(texts))}/{len(texts)}")

print("向量資料庫建立完成！")