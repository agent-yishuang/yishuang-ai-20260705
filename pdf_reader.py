import requests
import PyPDF2
import os

def read_pdf(file_path):
    """读取PDF文件内容"""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"读取PDF失败：{str(e)}"

def analyze_paper(text):
    """调用AI分析论文内容"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-538be27d9d6e4d1e95e6c9683967af02",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    prompt = f"""
    你是学术论文分析专家。请分析以下论文内容，按格式输出：

    1. 核心观点（3点，每点一句话）
    2. 创新点（2点，每点一句话）
    3. 提出3个帮助理解这篇论文的关键问题

    论文内容：{text[:3000]}
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

print("📄 PDF论文阅读助手启动！")
file_path = input("\n请拖入PDF文件路径：").strip().strip('"')

if not os.path.exists(file_path):
    print("❌ 文件不存在！请重新运行。")
    exit()

print("\n⏳ 正在读取PDF...")
text = read_pdf(file_path)

if len(text) < 50:
    print("❌ PDF内容太少或读取失败，请检查文件。")
    exit()

print("⏳ AI正在分析论文...")
summary = analyze_paper(text)

print("\n" + "="*40)
print("📝 论文分析结果：")
print("="*40)
print(summary)

input("\n按回车键退出...")