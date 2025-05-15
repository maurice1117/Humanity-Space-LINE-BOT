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
    # min_datetime = time.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    min_datetime = now
    min_datetime_str = min_datetime.strftime("%Y-%m-%dT%H:%M")
    print(min_datetime_str)
    max_datetime = now + timedelta(days=180, hours=23, minutes=59)
    max_datetime_str = max_datetime.strftime("%Y-%m-%dT%H:%M")  
    message = TemplateSendMessage(
        alt_text="請選擇預約時間",
        template=ButtonsTemplate(
            text="請選擇您的預約日期和時間：",
            actions=[
                DatetimePickerAction(
                    label="選擇日期和時間",
                    data=f"action=select_datetime&t={int(time.time())}",
                    mode="datetime",
                    initial=nowtime,
                    min=min_datetime_str,
                    max=max_datetime_str   
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


