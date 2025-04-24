import os
import uuid
import requests
import whisper

model = whisper.load_model("base")
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def download_audio(message_id: str, access_token: str) -> str:
    headers = { "Authorization": f"Bearer {access_token}" }
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    response = requests.get(url, headers=headers)
    file_path = os.path.join(AUDIO_DIR, f"{uuid.uuid4()}.m4a")
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]
