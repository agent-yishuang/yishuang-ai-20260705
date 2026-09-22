import requests
from bs4 import BeautifulSoup
import json


def search_baidu(query):
    url = f"https://www.baidu.com/s?wd={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('.result'):
            title = item.select_one('h3')
            if title:
                results.append(title.get_text(strip=True))
        return results[:5] if results else ["没有找到相关结果"]
    except Exception as e:
        return [f"搜索出错：{str(e)}"]


def ask_ai(question, search_results):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-538be27d9d6e4d1e95e6c9683967af02",
        "Content-Type": "application/json; charset=utf-8"
    }
    results_str = json.dumps(search_results, ensure_ascii=False)
    prompt = f"用户问题：{question}\n搜索结果：{results_str}\n请根据搜索结果回答用户的问题，用中文简洁回答。"
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]


print("🌐 AI联网搜索助手启动！输入'退出'结束。")
while True:
    question = input("\n你问：")
    if question == "退出":
        print("再见！")
        break
    print("🔍 正在搜索...")
    results = search_baidu(question)
    print("🤖 AI正在分析...")
    answer = ask_ai(question, results)
    print(f"\n💡 {answer}")