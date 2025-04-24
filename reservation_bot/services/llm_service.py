import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def is_reservation_request(text: str) -> bool:
    prompt = f"請判斷以下文字是否為餐廳預約相關訊息，回覆 '是' 或 '否'：\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }]
    )
    reply = response['choices'][0]['message']['content'].strip()
    return "是" in reply

def extract_reservation_info(text: str) -> dict:
    prompt = f'''
以下是一段使用者可能的預約訊息，請你擷取其中的以下資訊：
1. 姓名（name）
2. 電話（tel）
3. 預約日期與時間（date）
4. 特別備註（memo）例如吃素、過敏、生日等

回傳格式如下：
{{
  "name": "...",
  "tel": "...",
  "date": "...",
  "memo": "..."
}}

請分析這段訊息：
{text}
'''
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }]
    )
    reply = response['choices'][0]['message']['content']
    try:
        return json.loads(reply)
    except Exception:
        return {"name": "", "tel": "", "date": "", "memo": ""}