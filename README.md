# ⚖️ 中華民國刑法小幫手

基於 RAG（檢索增強生成）技術的刑法問答系統，提供法條查詢、引用與白話解釋。

## 功能
- 🔍 語意搜尋相關法條
- 📖 法條原文引用
- 💬 白話文解釋
- 🤖 自然語言問答

## 技術架構
| 元件 | 技術 |
|------|------|
| 前端介面 | Streamlit |
| 向量資料庫 | ChromaDB |
| Embedding 模型 | sentence-transformers |
| LLM | Groq（llama-3.3-70b） |
| 資料來源 | 中華民國刑法（全國法規資料庫） |

## 安裝與執行

### 1. Clone 專案
git clone https://github.com/你的帳號/criminal-law-rag.git
cd criminal-law-rag

### 2. 建立虛擬環境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

### 3. 安裝套件
pip install -r requirements.txt

### 4. 設定 API Key
建立 .env 檔案：
GROQ_API_KEY=你的Groq_API_Key

### 5. 建立向量資料庫
python build_vectordb.py

### 6. 啟動應用程式
streamlit run app_v1.py