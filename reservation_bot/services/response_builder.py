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
def build_host_query_flex() -> FlexSendMessage:
    flex_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                { "type": "text", "text": "老闆娘選單", "weight": "bold", "size": "lg" },
                {
                    "type": "button",
                    "action": { "type": "message", "label": "📅 查詢今日預約", "text": "查詢今天預約" },
                    "style": "primary"
                },
                {
                    "type": "button",
                    "action": { "type": "message", "label": "📅 查詢明日預約", "text": "查詢明天預約" },
                    "style": "primary"
                },
            ]
        }
    }

    return FlexSendMessage(alt_text="老闆娘選單", contents=flex_json)