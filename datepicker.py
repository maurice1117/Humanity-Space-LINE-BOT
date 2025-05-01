from linebot.models import DatetimePickerAction, PostbackAction, ButtonsTemplate, TextSendMessage, TemplateSendMessage
from linebot import LineBotApi
import os

from dotenv import load_dotenv
load_dotenv()
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN") )


# def send_datetime_picker(event):
#     message = TextSendMessage(
#         text="請選擇您的預約日期和時間：",
#         quick_reply={
#             "items": [
#                 DatetimePickerAction(
#                     label="選擇日期和時間",
#                     data="action=select_datetime",  # 傳送回的資料
#                     mode="datetime",
#                     initial="2025-04-21T10:00",
#                     max="2025-12-31T23:59",
#                     min="2025-04-21T00:00"
#                 )
#             ]
#         }
#     )
#     line_bot_api.reply_message(event.reply_token, message)

def send_datetime_picker(event):
    message = TemplateSendMessage(
        alt_text="請選擇預約時間",
        template=ButtonsTemplate(
            text="請選擇您的預約日期和時間：",
            actions=[
                DatetimePickerAction(
                    label="選擇日期和時間",
                    data="action=select_datetime",
                    mode="datetime",
                    initial="2025-04-21T10:00",
                    min="2025-04-21T00:00",
                    max="2025-12-31T23:59"
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)
    
