from openai import OpenAI
import os
from dotenv import load_dotenv
#import dateparser
from datetime import datetime
today = datetime.today().strftime("%Y/%m/%d")

# 載入 .env 環境變數
load_dotenv()

client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=os.getenv("TOGETHER_API_KEY")
)

# 測試文字
sample_text = "我姓陳，我想預約下禮拜一晚上十點，五個人，聚餐"

# 建立 prompt
prompt = f"""
你是一個 LINE Bot，用來協助餐廳紀錄預約資訊。請你從使用者的訊息中擷取資訊，並**只回傳 JSON 格式的內容**，不要解釋或教學。

若使用者的訊息中提及「今天」、「中午」、「今晚」、「明天」、「後天」、「這週五」、「下週二」、「這禮拜三」、「下禮拜四」等模糊時間，請**務必轉換為實際日期（格式為 YYYY/MM/DD）**。

- 請以今天 {today} 為基準進行推算。
- 請使用 UTC+8（台灣時區）作為基準。
- 請確保轉換後的日期對應到正確的星期幾，如果不確定，請重新確認，避免差到一天。（重要！）

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
