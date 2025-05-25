from linebot.models import TextSendMessage, FlexSendMessage
from linebot import LineBotApi
import os
import json

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

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
        try:
            # 嘗試將 user_text 當作 JSON 字串解析
            data = json.loads(user_text)

           # 建立欄位對應的中文名稱
            field_names = {
                "name": "姓名",
                "tel": "電話",
                "date": "日期",
                "預約目的": "目的",
                "分店": "分店",
                "memo": "備註"
            }
            
            # 動態組合訊息內容，只加上有提供的欄位
            reply_lines = ["✅ 預約資訊如下："]
            for key, label in field_names.items():
                if key in data:
                    reply_lines.append(f"{label}：{data[key]}")
    
            reply = "\n".join(reply_lines)

        except json.JSONDecodeError:
            reply = "❗請輸入正確的 JSON 格式"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
