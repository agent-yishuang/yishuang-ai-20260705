import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
API_KEY = "sk-538be27d9d6e4d1e95e6c9683967af02"

def search_news(keyword):
    url = f"https://www.baidu.com/s?wd={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('.result'):
            title = item.select_one('h3')
            if title:
                results.append(title.get_text(strip=True))
        return results[:10]
    except:
        return ["搜索失败"]

def summarize_with_ai(keyword, search_results):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    你是一个新闻编辑。请根据以下搜索结果，生成一份关于“{keyword}”的日报。
    
    搜索结果：
    {json.dumps(search_results, ensure_ascii=False)}
    
    要求：
    1. 标题：今日{keyword}热点
    2. 列出5条最重要的新闻，每条包含：标题、一句话摘要
    3. 格式为Markdown
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

def save_report(content, keyword):
    filename = f"{keyword}_日报_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 日报已保存为：{filename}")

print("📰 AI日报生成器启动！")
keyword = input("请输入你想追踪的关键词（比如：AI、科技、游戏）：")
print(f"🔍 正在搜索“{keyword}”相关新闻...")
results = search_news(keyword)
print(f"🤖 AI正在生成日报...")
report = summarize_with_ai(keyword, results)
print("\n" + "="*50)
print(report)
print("="*50)
save_report(report, keyword)
input("\n按回车键退出...")