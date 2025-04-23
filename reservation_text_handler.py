from linebot.models import TextSendMessage, FlexSendMessage
from linebot import LineBotApi
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

# 不用flex message確認預約了
def handle_text(event):
    user_text = event.message.text

    if user_text == "我要預約":
        flex_json = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "預約選單",
                        "weight": "bold",
                        "size": "lg"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "請選擇預約時段與人數：",
                        "wrap": True
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "今天 18:00（2人）",
                            "text": "我要預約 今天18:00 2人"
                        },
                        "style": "primary",
                        "color": "#905c44"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "今天 20:00（2人）",
                            "text": "我要預約 今天20:00 2人"
                        },
                        "style": "primary",
                        "color": "#905c44"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "明天 18:00（4人）",
                            "text": "我要預約 明天18:00 4人"
                        },
                        "style": "primary",
                        "color": "#905c44"
                    }
                ]
            }
        }

        message = FlexSendMessage(
            alt_text="請選擇預約時段與人數",
            contents=flex_json
        )

        line_bot_api.reply_message(event.reply_token, message)

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=user_text)
        )
