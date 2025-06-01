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
請從下列使用者訊息中擷取預約資訊，並**只回傳 JSON 格式結果**，不要加入其他說明或程式碼，格式如下：
- name（姓名）
- tel（電話）
- date（預約日期，格式"YYYY/MM/DD"）
- start_time（預約時間，格式"hh:mm:ss"，24小時制）
- branch（分店名稱，如果有的話，否則留空）
- memo（備註：如吃素、過敏、生日）

訊息如下：
{text}

請回傳以下格式（不要多加註解）：
{{
  "name": "...",
  "tel": "...",
  "date": "...",
  "start_time": "...",
  "branch": "...",
  "memo": "..."
}}

若無法擷取任何資訊，請回傳 False（注意：是字串 False，不是 JSON）
'''

    try:
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content.strip()
        print(f"🧾 Together.ai 回傳內容：\n{result}")

        if result.lower() == "false":
            print("📭 無法擷取資訊")
            return {
                "name": "",
                "tel": "",
                "date": "",
                "start_time": "",
                "branch": "",
                "memo": ""
            }

        # 嘗試抽取 JSON 部分
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("找不到 JSON 區段")

        json_str = result[json_start:json_end]
        data = json.loads(json_str)

        # 標準化：確保每個欄位都存在
        default_fields = ["name", "tel", "date", "start_time", "branch", "memo"]
        for field in default_fields:
            if field not in data:
                data[field] = ""

        return data

    except Exception as e:
        print(f"⚠️ 擷取 JSON 失敗：{e}")
        # if event:
        #     line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(text="🌟 看起來您有預約需求，但目前無法辨識完整資訊，請回傳以下格式\n姓名:\n電話:\n預約日期與時間(例: 2025/6/1 18:00):\n其他:")
        #     )
        return {
            "name": "",
            "tel": "",
            "date": "",
            "start_time": "",
            "branch": "",
            "memo": ""
        }