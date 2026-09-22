import requests


url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-538be27d9d6e4d1e95e6c9683967af02",
    "Content-Type": "application/json"
}


messages = [{"role": "system", "content": "你是一个乐于助人的AI助手。"}]


print("AI助手已启动！输入'退出'结束对话。")


while True:
    user_input = input("你：")
    if user_input == "退出":
        print("AI：再见啦！")
        break
    
    messages.append({"role": "user", "content": user_input})
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "stream": False
    }
    
    response = requests.post(url, headers=headers, json=data)
    ai_reply = response.json()["choices"][0]["message"]["content"]
    
    print("AI：" + ai_reply)
    messages.append({"role": "assistant", "content": ai_reply})