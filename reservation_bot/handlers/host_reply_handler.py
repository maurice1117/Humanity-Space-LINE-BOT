# 這個檔案專門用來處理老闆在收到預約相關訊息後加memo的部分。
# 老闆可以修改預約資訊或是刪除預約草稿，然後可以加上memo。原則上老闆用語音或文字都可以。
from services.host_control import is_host
from services.reservation_draft import confirm_draft, update_draft, delete_draft
from services.reservation_flow import finalize_and_save
from services.llm_service import is_reservation_request
from services.whisper_service import download_audio, transcribe_audio
from services.response_builder import text_reply
from linebot import LineBotApi
from linebot.models import AudioMessage, TextMessage
import os

from dotenv import load_dotenv
load_dotenv()

from handlers.text_handler import handle_text
from handlers.audio_handler import handle_audio

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
host_id = os.getenv("HOST_LINE_ID")
text = ""
def handle_host_reply(event):
    user_id = event.source.user_id

    if is_host(user_id):
        print(f"（管理者本人傳送💅）")

        # --------------------------------------------------
        # 判斷傳入的訊息「類型」、是否為「預約資訊」。
        #     是：傳給老闆確認
        #     否：進行罐頭回覆或自動回覆（已經分流但還沒做自動回覆）

        # 語音訊息
        if isinstance(event.message, AudioMessage):
            msg_type = "語音訊息"
            text = handle_audio(event)
        # 文字訊息
        elif isinstance(event.message, TextMessage):
            msg_type = "文字訊息"
            text = handle_text(event)
        # 無法判斷
        else:
            msg_type = "未知類型的訊息"
            text = "無"
        # 紀錄
        print(f"🔐 收到來自 {user_id} 的{msg_type}，內容: {text}")

        # ------------ 處理預約相關訊息 -------------
        if is_reservation_request(text):
            line_bot_api.reply_message(event.reply_token, text_reply(f"【預約】\n預約訊息：{text}"))
            line_bot_api.push_message(host_id, text_reply(f"🔔 使用者 {user_id} \n傳送{msg_type}：「{text}」"))
            line_bot_api.push_message(host_id, text_reply("請輸入預約資訊或操作指令，例如：\n1. 確認新增\n2. 修改\n3. 刪除\n4. 取消"))

            if isinstance(event.message, TextMessage):
                if text.startswith("確認新增"):
                    reservation = confirm_draft(user_id)
                    finalize_and_save(user_id, reservation)
                    line_bot_api.reply_message(event.reply_token, text_reply("✅ 已新增預約並通知使用者"))

                elif text.startswith("修改"):
                    _, key, value = text.split(" ", 2)
                    update_draft(user_id, **{key: value})
                    line_bot_api.reply_message(event.reply_token, text_reply(f"✏️ 已更新 {key} 為 {value}"))
                    line_bot_api.push_message(host_id, text_reply(f"🔔 使用者 {user_id} 修改 {key} 為 {value}"))

                elif text.startswith("刪除"):
                    delete_draft(user_id)
                    line_bot_api.reply_message(event.reply_token, text_reply("🗑 草稿已刪除"))
                    line_bot_api.push_message(host_id, text_reply(f"🔔 使用者 {user_id} 刪除預約草稿"))

                else:
                    line_bot_api.reply_message(event.reply_token, text_reply("無法辨識操作"))
        else:
            line_bot_api.reply_message(event.reply_token, text_reply(f"【非預約】\n訊息：{text}"))
