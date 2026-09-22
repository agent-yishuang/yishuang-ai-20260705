import gradio as gr
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

API_KEY = "sk-538be27d9d6e4d1e95e6c9683967af02"
API_URL = "https://api.deepseek.com/v1/chat/completions"

# ========== 通用工具 ==========
def call_ai(prompt):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "stream": False}
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

def search_web(query):
    url = f"https://www.baidu.com/s?wd={query}"
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
        return results[:8]
    except:
        return ["搜索失败"]

# ========== 功能 1：AI 聊天 ==========
def chat_fn(message, history):
    return call_ai(message)

# ========== 功能 2：日报生成 ==========
def daily_report_fn(keyword):
    if not keyword.strip(): return "请输入关键词"
    results = search_web(keyword)
    prompt = f"你是新闻编辑，根据以下搜索结果生成关于'{keyword}'的Markdown日报，包含5条新闻：\n{json.dumps(results, ensure_ascii=False)}"
    return call_ai(prompt)

# ========== 功能 3：多步骤 Agent ==========
def agent_fn(user_goal):
    if not user_goal.strip(): return "请输入任务"
    log = f"🎯 任务：{user_goal}\n\n"
    history = []
    for step in range(4):
        prompt = f"你是智能助手。可调用工具：search_web(搜索)、save_file(保存)、calculate(计算)、finish(完成)。\n总目标：{user_goal}\n已执行：{history}\n严格按JSON返回：{{\"tool\": \"工具名\", \"input\": \"输入\", \"reason\": \"原因\"}}\n如果完成，tool用finish。"
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "stream": False}
        response = requests.post(API_URL, headers=headers, json=data)
        ai_reply = response.json()["choices"][0]["message"]["content"]
        try:
            start = ai_reply.find("{"); end = ai_reply.rfind("}") + 1
            decision = json.loads(ai_reply[start:end])
        except:
            decision = {"tool": "finish", "input": ai_reply, "reason": "解析失败"}
        tool = decision.get("tool"); tool_input = decision.get("input", ""); reason = decision.get("reason", "")
        log += f"--- 第 {step+1} 步 ---\n🤔 思考：{reason}\n"
        if tool == "finish":
            log += f"\n✅ 任务完成！\n最终结果：{tool_input}"
            return log
        if tool == "search_web": result = f"搜索到关于'{tool_input}'的资料"
        elif tool == "save_file": result = f"已保存：{tool_input[:50]}..."
        elif tool == "calculate":
            try: result = f"计算结果：{eval(tool_input)}"
            except: result = "计算失败"
        else: result = f"未知工具：{tool}"
        log += f"🔧 调用：{tool}\n📤 结果：{result}\n\n"
        history.append(f"{tool}({tool_input[:30]}) → {result}")
    log += "\n⚠️ 达到最大步数，任务终止。"
    return log

# ========== 功能 4：PDF 阅读助手 ==========
def pdf_summary(file):
    if file is None: return "请上传 PDF 文件"
    try:
        import PyPDF2
        with open(file.name, 'rb') as f:
            reader = PyPDF2.PdfReader(f); text = ""
            for page in reader.pages: text += page.extract_text()
        return call_ai(f"请总结以下文档的核心内容，列出3个要点：\n{text[:3000]}")
    except Exception as e: return f"读取失败：{e}"

# ========== 功能 5：问卷数据分析 ==========
def survey_analysis(file):
    if file is None: return "请上传 Excel/CSV 文件"
    try:
        import pandas as pd
        if file.name.endswith('.csv'): df = pd.read_csv(file.name)
        else: df = pd.read_excel(file.name)
        info = f"📊 数据概览\n行数：{len(df)}\n列数：{len(df.columns)}\n\n列名：{df.columns.tolist()}\n\n前5行：\n{df.head().to_string()}\n\n"
        prompt = f"请分析以下问卷数据，给出关键洞察：\n{df.describe().to_string()}"
        info += f"\n🤖 AI 分析：\n{call_ai(prompt)}"
        return info
    except Exception as e: return f"分析失败：{e}"

# ========== 功能 6：网页摘要 ==========
def web_summary(url):
    if not url.strip(): return "请输入网址"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()[:3000]
        return call_ai(f"请用中文总结以下网页内容，列出3个核心要点：\n{text}")
    except Exception as e: return f"抓取失败：{e}"

# ========== 功能 7：邮件撰写 ==========
def email_writer(purpose):
    if not purpose.strip(): return "请输入邮件目的"
    return call_ai(f"请帮我写一封专业的邮件，目的：{purpose}。要求：语气正式，结构清晰。")

# ========== 功能 8：代码解释 ==========
def code_explain(code):
    if not code.strip(): return "请输入代码"
    return call_ai(f"请解释以下代码的功能、关键逻辑和优化点：\n{code}")

# ========== 功能 9：翻译助手 ==========
def translate(text, target):
    if not text.strip(): return "请输入要翻译的内容"
    return call_ai(f"请把以下内容翻译成{target}，保持原意：\n{text}")

# ========== 功能 10：创意命名 ==========
def naming(desc):
    if not desc.strip(): return "请输入描述"
    return call_ai(f"请为以下内容生成10个有创意的中文名字，并说明含义：\n{desc}")

# ========== 功能 11：面试问题生成 ==========
def interview_qs(job):
    if not job.strip(): return "请输入岗位名称"
    return call_ai(f"请为'{job}'岗位生成10个高频面试问题，并给出简要的答题思路。")

# ========== 功能 12：简历润色 ==========
def resume_polish(text):
    if not text.strip(): return "请输入简历内容"
    return call_ai(f"请帮我润色以下简历内容，让它更专业、更简洁，突出亮点：\n{text}")

# ========== 功能 13：周报生成 ==========
def weekly_report(work):
    if not work.strip(): return "请输入本周工作内容"
    return call_ai(f"请根据以下工作内容，生成一份结构清晰的周报，包含：本周完成、遇到的问题、下周计划：\n{work}")

# ========== 功能 14：小红书文案 ==========
def xiaohongshu(topic):
    if not topic.strip(): return "请输入主题"
    return call_ai(f"请为'{topic}'写一篇小红书风格的文案，包含标题、正文、3-5个emoji、相关标签。")

# ========== 功能 15：短视频脚本 ==========
def video_script(topic):
    if not topic.strip(): return "请输入主题"
    return call_ai(f"请为'{topic}'写一个30秒短视频脚本，包含：开头3秒钩子、正文、结尾引导关注。")

# ========== 功能 16：学习计划 ==========
def study_plan(subject):
    if not subject.strip(): return "请输入学习目标"
    return call_ai(f"我想学习'{subject}'，请帮我制定一个为期4周的学习计划，每周列出具体任务。")

# ========== 功能 17：SQL 生成 ==========
def sql_gen(requirement):
    if not requirement.strip(): return "请输入需求描述"
    return call_ai(f"请根据以下需求，写一条SQL查询语句，并解释每个部分的作用：\n{requirement}")

# ========== 功能 18：正则表达式生成 ==========
def regex_gen(desc):
    if not desc.strip(): return "请输入匹配需求"
    return call_ai(f"请为以下需求生成Python正则表达式，并解释含义：\n{desc}")

# ========== 功能 19：LLM 提示词优化 ==========
def prompt_optimize(prompt):
    if not prompt.strip(): return "请输入原始提示词"
    return call_ai(f"请帮我优化以下LLM提示词，让它更清晰、更具体、效果更好：\n{prompt}")

# ========== 功能 20：数据可视化建议 ==========
def chart_suggest(data_desc):
    if not data_desc.strip(): return "请输入数据描述"
    return call_ai(f"我有以下数据，请推荐最合适的可视化图表类型，并说明理由：\n{data_desc}")

# ========== 构建界面 ==========
with gr.Blocks(title="AI 全能工具箱") as demo:
    gr.Markdown("# 🤖 AI 全能工具箱（20 大功能）")
    gr.Markdown("集成了 20 个实用 AI 功能。")

    with gr.Tabs():
        with gr.Tab("💬 AI 聊天"):
            chatbot = gr.Chatbot(label="对话历史")
            msg = gr.Textbox(label="你的问题")
            def respond(message, chat_history):
                bot_message = chat_fn(message, chat_history)
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": bot_message})
                return "", chat_history
            msg.submit(respond, [msg, chatbot], [msg, chatbot])

        with gr.Tab("📰 日报生成"):
            kw_input = gr.Textbox(label="关键词"); report_btn = gr.Button("生成日报"); report_output = gr.Markdown()
            report_btn.click(daily_report_fn, inputs=kw_input, outputs=report_output)

        with gr.Tab("🤖 多步骤 Agent"):
            goal_input = gr.Textbox(label="你的任务"); agent_btn = gr.Button("启动 Agent"); agent_output = gr.Textbox(label="执行日志", lines=15)
            agent_btn.click(agent_fn, inputs=goal_input, outputs=agent_output)

        with gr.Tab("📄 PDF 阅读"):
            pdf_file = gr.File(label="上传 PDF", file_types=[".pdf"]); pdf_btn = gr.Button("分析 PDF"); pdf_output = gr.Textbox(label="结果", lines=10)
            pdf_btn.click(pdf_summary, inputs=pdf_file, outputs=pdf_output)

        with gr.Tab("📊 问卷分析"):
            survey_file = gr.File(label="上传 Excel/CSV", file_types=[".xlsx", ".csv"]); survey_btn = gr.Button("分析数据"); survey_output = gr.Textbox(label="结果", lines=10)
            survey_btn.click(survey_analysis, inputs=survey_file, outputs=survey_output)

        with gr.Tab("🌐 网页摘要"):
            url_input = gr.Textbox(label="网页网址"); web_btn = gr.Button("总结网页"); web_output = gr.Textbox(label="摘要", lines=10)
            web_btn.click(web_summary, inputs=url_input, outputs=web_output)

        with gr.Tab("✉️ 邮件撰写"):
            email_input = gr.Textbox(label="邮件目的"); email_btn = gr.Button("生成邮件"); email_output = gr.Textbox(label="邮件内容", lines=10)
            email_btn.click(email_writer, inputs=email_input, outputs=email_output)

        with gr.Tab("💻 代码解释"):
            code_input = gr.Textbox(label="粘贴代码", lines=5); code_btn = gr.Button("解释代码"); code_output = gr.Textbox(label="解释", lines=10)
            code_btn.click(code_explain, inputs=code_input, outputs=code_output)

        with gr.Tab("🌍 翻译助手"):
            trans_input = gr.Textbox(label="要翻译的内容", lines=3)
            trans_target = gr.Dropdown(choices=["英文", "日文", "韩文", "法文", "德文"], label="目标语言", value="英文")
            trans_btn = gr.Button("翻译"); trans_output = gr.Textbox(label="翻译结果", lines=5)
            trans_btn.click(translate, inputs=[trans_input, trans_target], outputs=trans_output)

        with gr.Tab("✨ 创意命名"):
            name_input = gr.Textbox(label="描述"); name_btn = gr.Button("生成名字"); name_output = gr.Textbox(label="名字列表", lines=10)
            name_btn.click(naming, inputs=name_input, outputs=name_output)

        with gr.Tab("🎤 面试问题"):
            job_input = gr.Textbox(label="岗位名称"); job_btn = gr.Button("生成问题"); job_output = gr.Textbox(label="问题列表", lines=12)
            job_btn.click(interview_qs, inputs=job_input, outputs=job_output)

        with gr.Tab("📝 简历润色"):
            resume_input = gr.Textbox(label="简历内容", lines=5); resume_btn = gr.Button("润色"); resume_output = gr.Textbox(label="润色后", lines=10)
            resume_btn.click(resume_polish, inputs=resume_input, outputs=resume_output)

        with gr.Tab("📅 周报生成"):
            work_input = gr.Textbox(label="本周工作", lines=5); work_btn = gr.Button("生成周报"); work_output = gr.Textbox(label="周报", lines=10)
            work_btn.click(weekly_report, inputs=work_input, outputs=work_output)

        with gr.Tab("📱 小红书文案"):
            xhs_input = gr.Textbox(label="主题"); xhs_btn = gr.Button("生成文案"); xhs_output = gr.Textbox(label="文案", lines=10)
            xhs_btn.click(xiaohongshu, inputs=xhs_input, outputs=xhs_output)

        with gr.Tab("🎬 短视频脚本"):
            video_input = gr.Textbox(label="主题"); video_btn = gr.Button("生成脚本"); video_output = gr.Textbox(label="脚本", lines=10)
            video_btn.click(video_script, inputs=video_input, outputs=video_output)

        with gr.Tab("📚 学习计划"):
            study_input = gr.Textbox(label="学习目标"); study_btn = gr.Button("生成计划"); study_output = gr.Textbox(label="计划", lines=10)
            study_btn.click(study_plan, inputs=study_input, outputs=study_output)

        with gr.Tab("🗄️ SQL 生成"):
            sql_input = gr.Textbox(label="需求描述", lines=3); sql_btn = gr.Button("生成SQL"); sql_output = gr.Textbox(label="SQL", lines=8)
            sql_btn.click(sql_gen, inputs=sql_input, outputs=sql_output)

        with gr.Tab("🔍 正则表达式"):
            regex_input = gr.Textbox(label="匹配需求"); regex_btn = gr.Button("生成正则"); regex_output = gr.Textbox(label="正则表达式", lines=5)
            regex_btn.click(regex_gen, inputs=regex_input, outputs=regex_output)

        with gr.Tab("🎯 提示词优化"):
            prompt_input = gr.Textbox(label="原始提示词", lines=4); prompt_btn = gr.Button("优化"); prompt_output = gr.Textbox(label="优化后", lines=8)
            prompt_btn.click(prompt_optimize, inputs=prompt_input, outputs=prompt_output)

        with gr.Tab("📈 图表推荐"):
            chart_input = gr.Textbox(label="数据描述", lines=3); chart_btn = gr.Button("推荐图表"); chart_output = gr.Textbox(label="推荐结果", lines=8)
            chart_btn.click(chart_suggest, inputs=chart_input, outputs=chart_output)

demo.launch()