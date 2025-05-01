from linebot.models import DatetimePickerAction, PostbackAction, ButtonsTemplate,TemplateSendMessage
from linebot import LineBotApi
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN") )

## 可以選擇時間
def send_datetime_picker(event):
    now = datetime.now()
    nowtime = now.strftime("%Y-%m-%dT%H:%M")
    min_datetime = time.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    max_datetime = nowtime+timedelta(days=180, hours=23, minutes=59)
    message = TemplateSendMessage(
        alt_text="請選擇預約時間",
        template=ButtonsTemplate(
            text="請選擇您的預約日期和時間：",
            actions=[
                DatetimePickerAction(
                    label="選擇日期和時間",
                    data="action=select_datetime",
                    mode="datetime",
                    initial=nowtime,
                    min=min_datetime.strftime("%Y-%m-%dT%H:%M"),
                    max=max_datetime.strftime("%Y-%m-%dT%H:%M")
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)


# @handler.add(PostbackEvent)

# def handle_postback(event):
    
#     data = event.data
#     selected_time = event.postback.params.get("datetime")

#     if selected_time:
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=f"你選擇的時間是：{selected_time}")
#         )


