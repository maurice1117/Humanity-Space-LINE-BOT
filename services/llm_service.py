from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# 初始化 Together.ai client
client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1"
)

def is_reservation_request(text: str) -> bool:
    print("🧠 Together.ai 正在判斷是否為預約訊息...")
    prompt = f"請判斷以下訊息是否與預約相關，僅回答 True 或 False：\n{text}\n回答："

    try:
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip().lower()
        return result == "true"
    except Exception as e:
        print(f"⚠️ 判斷預約意圖失敗：{e}")
        return False

def extract_reservation_info(text: str) -> dict:
    print("🔍 Together.ai 正在擷取預約資訊...")
    prompt = f'''
請根據以下使用者訊息，擷取預約資訊並回傳 JSON 格式，包含：
- name（姓名）
- tel（電話）
- date（預約時間與日期）
- memo（備註，如吃素、過敏、生日）

訊息如下：
{text}

請回傳以下格式：
{{
  "name": "...",
  "tel": "...",
  "date": "...",
  "memo": "..."
}}

若找不到資訊，請回傳：False
'''

    try:
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()

        if result.lower() == "false":
            return {
                "name": "",
                "tel": "",
                "date": "",
                "memo": ""
            }

        # 嘗試解析 JSON
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        json_str = result[json_start:json_end]
        return json.loads(json_str)

    except Exception as e:
        print(f"⚠️ 擷取 JSON 失敗：{e}")
        return {
            "name": "",
            "tel": "",
            "date": "",
            "memo": ""
        }
