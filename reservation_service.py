from linebot.models import TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction
from linebot import LineBotApi
import os

from dotenv import load_dotenv
load_dotenv()


line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")  # 或你可以寫入白名單驗證函式

def notify_admin(reservation_data, user_id):
    try:
        print(f"推送訊息給管理員，使用者 ID: {ADMIN_USER_ID}")
        message = TemplateSendMessage(
            alt_text='新的預約請求',
            template=ButtonsTemplate(
                title='新的預約請求',
                text=(
                    f"時間：{reservation_data['time']}\n"
                    f"人數：{reservation_data['people']}\n"
                    f"目的：{reservation_data['purpose']}\n"
                    f"備註：{reservation_data['note']}"
                ),
                actions=[
                    MessageAction(label='✅ 接受', text=f"接受預約:{user_id}"),
                    MessageAction(label='❌ 拒絕', text=f"拒絕預約:{user_id}")
                ]
            )
        )
        if not ADMIN_USER_ID: # 卡在這一步
            raise ValueError("ADMIN_USER_ID 未設定或錯誤，請檢查環境變數")
        line_bot_api.push_message(ADMIN_USER_ID, message)
    except Exception as e:
        print(f"推送訊息失敗：{e}")
