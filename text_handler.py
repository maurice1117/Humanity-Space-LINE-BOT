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

            # 檢查
            required_fields = ["name", "tel", "date", "預約目的", "分店", "memo"]
            if all(field in data for field in required_fields):
                reply = (
                    f"✅ 預約資訊如下：\n"
                    f"姓名：{data['name']}\n"
                    f"電話：{data['tel']}\n"
                    f"日期：{data['date']}\n"
                    f"目的：{data['預約目的']}\n"
                    f"分店：{data['分店']}\n"
                    f"備註：{data['memo']}"
                )
            else:
                reply = "❗JSON 格式缺少必要欄位，請確認是否有：name, tel, date, 預約目的, 分店, memo"

        except json.JSONDecodeError:
            reply = "❗請輸入正確的 JSON 格式（包含 name, tel, date, 預約目的, 分店, memo）"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
