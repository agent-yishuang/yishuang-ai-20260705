import os
import PyPDF2
import chromadb
import requests
import json
API_KEY = "sk-538be27d9d6e4d1e95e6c9683967af02"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_EMBED_URL = "https://api.deepseek.com/v1/embeddings"
DOCS_DIR = "./documents"
CHROMA_DIR = "./chroma_db_deepseek"

# ========== 用 DeepSeek 做文本嵌入 ==========
def get_embedding(text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-embedding",
        "input": text[:1000]  # 限制长度
    }
    try:
        response = requests.post(DEEPSEEK_EMBED_URL, headers=headers, json=data)
        return response.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"❌ 嵌入失败：{e}")
        return None

# ========== 读取PDF ==========
def read_pdfs():
    texts = []
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"📁 请把PDF文件放进 {DOCS_DIR} 文件夹")
        return texts
    for file in os.listdir(DOCS_DIR):
        if file.endswith(".pdf"):
            path = os.path.join(DOCS_DIR, file)
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                texts.append(text[:2000])
                print(f"✅ 已读取：{file}")
    return texts

# ========== 创建向量数据库 ==========
def create_vector_store(texts):
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("docs")
    for i, text in enumerate(texts):
        embedding = get_embedding(text)
        if embedding:
            collection.add(
                documents=[text],
                embeddings=[embedding],
                ids=[f"doc_{i}"]
            )
    print(f"✅ 向量数据库创建完成，共 {len(texts)} 个文档")
    return collection

# ========== 检索 ==========
def search(collection, query, top_k=2):
    query_embedding = get_embedding(query)
    if not query_embedding:
        return ["检索失败"]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results['documents'][0]

# ========== 调用 AI 生成答案 ==========
def ask_ai(question, context):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"参考资料：{context}\n\n用户问题：{question}\n请根据参考资料用中文回答。"
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    response = requests.post(DEEPSEEK_URL, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# ========== 主程序 ==========
def main():
    print("📚 DeepSeek 版 RAG 知识库")
    texts = read_pdfs()
    if not texts:
        return
    collection = create_vector_store(texts)
    while True:
        q = input("\n❓ 你问：")
        if q == "退出":
            break
        print("🔍 正在检索...")
        context = search(collection, q)
        print("🤖 AI正在生成答案...")
        answer = ask_ai(q, context)
        print(f"💡 回答：{answer}")

if __name__ == "__main__":
    main()