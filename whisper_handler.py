# whisper_handler.py
import os
import uuid
import requests
import whisper

from linebot.models import TextSendMessage, FlexSendMessage
from linebot import LineBotApi

from types import SimpleNamespace
from text_handler import handle_text

# 載入 Whisper 模型（建議先用 base）
model = whisper.load_model("base")

# 儲存音訊的資料夾
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def download_audio(message_id: str, access_token: str) -> str:
    """
    從 LINE API 下載語音檔，並儲存為 m4a
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"語音下載失敗: {resp.status_code}")
    file_path = os.path.join(AUDIO_DIR, f"{uuid.uuid4()}.m4a")
    with open(file_path, "wb") as f:
        f.write(resp.content)
    return file_path

def transcribe_audio(file_path: str) -> str:
    """
    使用 Whisper 將 m4a 轉為文字
    """
    result = model.transcribe(file_path)
    return result.get("text", "").strip()

def handle_audio_event(event, access_token: str):
    """
    整合下載、轉寫，並把結果傳給 text_handler 處理
    """
    # 1. 下載
    audio_path = download_audio(event.message.id, access_token)
    # 2. 轉寫
    transcript = transcribe_audio(audio_path)
    # 3. 將原本的 audio event 改成「只有 text 屬性」的簡易物件
    event.message = SimpleNamespace(text=transcript)
    # 4. 呼叫文字處理器
    handle_text(event)
