import openai
import os
import json

# 設定 Together.ai API
openai.api_base = "https://api.together.xyz/v1"
openai.api_key = os.getenv("TOGETHER_API_KEY")

def is_reservation_request(text: str) -> bool:
    print(f"together.ai 正在判斷預約需求")
    prompt = f"請判斷以下訊息是否與預約相關，回答True或False：\n{text}\n回答："
    response = openai.ChatCompletion.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response['choices'][0]['message']['content'].strip().lower()
    return result == "true"

def extract_reservation_info(text: str) -> dict:
    prompt = f'''
請根據以下使用者訊息，試著擷取以下預約資訊並回傳 JSON 格式：
- name（姓名）
- tel（電話）
- date（預約時間與日期）
- memo（備註：如吃素、過敏、生日、很吵）
訊息如下：
{text}

請回傳以下格式：
{{
  "name": "...",
  "tel": "...",
  "date": "...",
  "memo": "...",

}}

若沒有相關資訊，請回傳False。
'''
    response = openai.ChatCompletion.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response['choices'][0]['message']['content']
    try:
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        json_str = result[json_start:json_end]
        return json.loads(json_str)
    except Exception:
        return {{
  "name": "...",
  "tel": "...",
  "date": "...",
  "memo": "...",

}}