# response_builder.py
from linebot.models import TextSendMessage, FlexSendMessage

def text_reply(text: str) -> TextSendMessage:
    return TextSendMessage(text=text)

def build_reservation_flex(reservation: dict) -> FlexSendMessage:
    name = reservation.get("name", "未知")
    tel = reservation.get("tel", "未提供")
    date = reservation.get("date", "未提供")
    memo = reservation.get("memo", "無")

    flex_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                { "type": "text", "text": "新的預約申請", "weight": "bold", "size": "lg" },
                { "type": "text", "text": f"姓名：{name}" },
                { "type": "text", "text": f"電話：{tel}" },
                { "type": "text", "text": f"日期：{date}" },
                { "type": "text", "text": f"備註：{memo}" },
                {
                    "type": "button",
                    "action": { "type": "message", "label": "✅ 確認新增", "text": "確認新增" },
                    "style": "primary"
                },
                {
                    "type": "button",
                    "action": { "type": "message", "label": "📑 修改", "text": "修改" },
                    "style": "secondary"
                },
                {
                    "type": "button",
                    "action": { "type": "message", "label": "❌ 刪除", "text": "刪除" },
                    "style": "secondary"
                }
            ]
        }
    }

    return FlexSendMessage(alt_text="預約審核通知", contents=flex_json)

def build_dynamic_reservation_reply(data: dict) -> str:
    """
    動態組合回覆文字：只顯示有提供的欄位
    """
    field_names = {
        "name": "姓名",
        "tel": "電話",
        "date": "日期",
        "預約目的": "目的",
        "分店": "分店",
        "memo": "備註"
    }

    reply_lines = ["✅ 已接收以下預約資訊："]
    for key, label in field_names.items():
        if key in data:
            reply_lines.append(f"{label}：{data[key]}")

    # 若 JSON 中沒有任何可顯示欄位，就提示使用者
    if len(reply_lines) == 1:
        reply_lines.append("⚠️ 目前沒有任何可顯示的欄位，請再確認格式！")

    return "\n".join(reply_lines)
