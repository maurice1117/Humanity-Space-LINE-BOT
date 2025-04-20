import os
import requests
import uuid
import whisper

# Whisper 模型（建議先用 base）
model = whisper.load_model("base")

# 儲存音訊的資料夾
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def download_audio(message_id: str, access_token: str) -> str:
    """
    從 LINE 的 API 下載語音檔案並儲存為 m4a
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception("語音下載失敗")

    file_path = os.path.join(AUDIO_DIR, f"{uuid.uuid4()}.m4a")
    with open(file_path, "wb") as f:
        f.write(response.content)
    
    return file_path

def transcribe_audio(file_path: str) -> str:
    """
    使用 Whisper 將 m4a 音檔轉為文字
    """
    result = model.transcribe(file_path)
    return result["text"]
