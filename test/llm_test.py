from openai import OpenAI
import os
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

# 初始化 OpenAI 客戶端（針對 Together AI）
client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1"
)

# 測試文字
sample_text = "我是林小姐，電話是0912345678，想預約5月1日下午三點，吃素，怕辣。"

# 建立 prompt
prompt = f"""
你是一個 LINE Bot，用來協助餐廳紀錄預約資訊，請你從使用者的訊息中擷取資訊，並只回傳 JSON 格式的內容，不要解釋或教學。

訊息如下：
{sample_text}

請回傳以下格式：
{{
  "name": "...",
  "tel": "...",
  "date": "...",
  "memo": "..."
}}
"""

# 呼叫 Together AI 的 Mistral 模型
response = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.1",
    messages=[{"role": "user", "content": prompt}]
)

# 印出模型回傳內容
print(response.choices[0].message.content)
