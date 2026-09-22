import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

API_KEY = "sk-538be27d9d6e4d1e95e6c9683967af02"  # 记得换成你自己的
API_URL = "https://api.deepseek.com/v1/chat/completions"

# ========== 工具层 ==========
def search_web(query):
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
        return "搜索结果：\n" + "\n".join(results[:5]) if results else "没有找到相关结果"
    except Exception as e:
        return f"搜索出错：{str(e)}"

def save_file(content):
    filename = f"agent_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已保存到 {filename}"

def calculate(expression):
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except:
        return "计算失败，请检查表达式"

TOOLS = {
    "search_web": search_web,
    "save_file": save_file,
    "calculate": calculate
}

# ========== AI 规划层 ==========
def plan_task(user_goal):
    prompt = f"""
    你是一个任务规划专家。用户的目标是：{user_goal}
    请把这个任务拆解成 2-5 个具体步骤，每步用一句话描述。
    输出格式：直接返回步骤列表，每行一步，不要编号。
    """
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "stream": False}
    response = requests.post(API_URL, headers=headers, json=data)
    plan = response.json()["choices"][0]["message"]["content"]
    return [line.strip() for line in plan.strip().split("\n") if line.strip()]

# ========== AI 决策层 ==========
def decide_next_step(user_goal, plan, history):
    prompt = f"""
    你是智能助手，可以调用以下工具：
    - search_web: 搜索网页
    - save_file: 保存内容到文件
    - calculate: 计算数学表达式
    - finish: 任务完成

    总目标：{user_goal}
    计划步骤：{plan}
    已执行记录：{history}

    请决定下一步做什么，严格按JSON返回：
    {{"tool": "工具名", "input": "工具输入", "reason": "原因", "status": "进行中/已完成"}}

    如果已完成，tool 用 finish，status 用 已完成。
    """
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "stream": False}
    response = requests.post(API_URL, headers=headers, json=data)
    ai_reply = response.json()["choices"][0]["message"]["content"]
    try:
        start = ai_reply.find("{")
        end = ai_reply.rfind("}") + 1
        return json.loads(ai_reply[start:end])
    except:
        return {"tool": "finish", "input": ai_reply, "reason": "解析失败", "status": "已完成"}

# ========== AI 反思层 ==========
def reflect(user_goal, step_result):
    prompt = f"""
    目标：{user_goal}
    刚刚的执行结果：{step_result}
    请评估：这个结果是否有助于达成目标？
    只需回答：满意 或 不满意
    """
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "stream": False}
    response = requests.post(API_URL, headers=headers, json=data)
    result = response.json()["choices"][0]["message"]["content"].strip()
    return "满意" in result

# ========== Agent 主循环 ==========
def run_agent(user_goal):
    print(f"\n{'='*50}")
    print(f"🎯 任务：{user_goal}")
    print(f"{'='*50}")

    print("\n📋 正在规划任务...")
    plan = plan_task(user_goal)
    print("规划步骤：")
    for i, step in enumerate(plan, 1):
        print(f"  {i}. {step}")

    history = []
    max_steps = 6

    for step_num in range(max_steps):
        print(f"\n--- 第 {step_num + 1} 步 ---")
        decision = decide_next_step(user_goal, plan, history)
        tool_name = decision.get("tool")
        tool_input = decision.get("input")
        reason = decision.get("reason", "")
        status = decision.get("status", "")

        print(f"🤔 思考：{reason}")

        if tool_name == "finish" or status == "已完成":
            print(f"\n✅ 任务完成！")
            print(f"最终结果：{tool_input}")
            return tool_input

        if tool_name in TOOLS:
            print(f"🔧 调用工具：{tool_name}")
            result = TOOLS[tool_name](tool_input)
            print(f"📤 结果：{result[:200]}...")
            history.append(f"步骤{step_num+1}：{tool_name}({tool_input}) → {result[:100]}")

            print("🧠 正在评估结果...")
            if reflect(user_goal, result):
                print("✅ 结果满意，继续推进")
            else:
                print("⚠️ 结果不理想，可能需要调整策略")
        else:
            print(f"⚠️ 未知工具：{tool_name}")
            history.append(f"步骤{step_num+1}：未知工具 {tool_name}")

    print("\n⚠️ 达到最大步数，任务终止。")

# ========== 主程序 ==========
print("🚀 顶级 AI Agent 已启动！")
print("试试这些复杂任务：")
print("  - 搜索今天AI新闻，总结后保存到文件")
print("  - 计算 (25*4+10)*2，然后保存结果")
print("  - 搜索天气，分析后保存")

while True:
    goal = input("\n🎯 你的任务：")
    if goal == "退出":
        break
    run_agent(goal)