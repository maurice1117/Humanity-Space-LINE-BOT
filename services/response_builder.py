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

## NEW
def notify_before_one_day(reservation) -> FlexSendMessage:
    
    name = reservation.get("name", "貴賓")
    branch = reservation.get("branch", "TBD")
    date = reservation.get("date", "日期未知")
    start_time = reservation.get("start_time", "時間未知")
    
    notify_text_json = {
    "type": "bubble",
    "hero": {
        "type": "image",
        "url": "https://developers-resource.landpress.line.me/fx/img/01_3_movie.png",
        "size": "full",
        "aspectRatio": "20:13",
        "aspectMode": "cover",
        "action": {
        "type": "uri",
        "uri": "https://line.me/"
        }
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "spacing": "md",
        "contents": [
        {
            "type": "text",
            "text": "預約提醒",
            "wrap": True,
            "weight": "bold",
            "gravity": "center",
            "size": "xl"
        },
        {
            "type": "text",
            "text": f"親愛的貴賓{name}您好～",
            "size": "md"
        },
        {
            "type": "text",
            "text": "以下是您的預約資訊："
        },
        {
            "type": "box",
            "layout": "vertical",
            "margin": "lg",
            "spacing": "sm",
            "contents": [
            {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                {
                    "type": "text",
                    "text": "分店",
                    "color": "#aaaaaa",
                    "size": "sm",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": branch,
                    "wrap": True,
                    "color": "#666666",
                    "size": "sm",
                    "flex": 4
                }
                ]
            },
            {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                {
                    "type": "text",
                    "text": "日期",
                    "color": "#aaaaaa",
                    "size": "sm",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": date,
                    "wrap": True,
                    "size": "sm",
                    "color": "#666666",
                    "flex": 4
                }
                ]
            },
            {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                {
                    "type": "text",
                    "text": "時間",
                    "color": "#aaaaaa",
                    "size": "sm",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": start_time ,
                    "wrap": True,
                    "color": "#666666",
                    "size": "sm",
                    "flex": 4
                }
                ]
            }
            ]
        }
        ]
    }
    }
    return FlexSendMessage(alt_text="預約提醒", contents=notify_text_json)

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
