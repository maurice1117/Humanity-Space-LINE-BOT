import openai
import os

# 設定 Together.ai API
openai.api_base = "https://api.together.xyz/v1"
openai.api_key = os.getenv("TOGETHER_API_KEY")

def enrich_with_rag(reservation: dict, rag_file="data/人性空間資訊.txt") -> dict:
    try:
        with open(rag_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return reservation

    user_name = reservation.get("name", "")
    user_tel = reservation.get("tel", "")
    enriched_note = reservation.get("memo", "")

    related_info = "\n".join([line.strip() for line in lines if user_name in line or user_tel in line])
    if related_info:
        prompt = f"""
你是一個 LINE Bot，負責補強預約資訊。根據以下資料，幫我補充一段備註，語氣自然且有資訊價值。只輸出備註內容，不要解釋。

資料如下：
{related_info}

請輸出補充備註內容：
"""
        response = openai.ChatCompletion.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response['choices'][0]['message']['content'].strip()
        enriched_note += f"；補充資料：{reply}"

    reservation["memo"] = enriched_note
    return reservation