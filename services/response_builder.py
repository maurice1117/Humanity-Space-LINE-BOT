# response_builder.py
from linebot.models import TextSendMessage, FlexSendMessage

def text_reply(text: str) -> TextSendMessage:
    return TextSendMessage(text=text)
# 預約訊息
def build_reservation_flex(reservation: dict) -> FlexSendMessage:
    name = reservation.get("name", "未知")
    tel = reservation.get("tel", "未提供")
    date = reservation.get("date", "未提供")
    start_time = reservation.get("start_time", "未提供")
    branch = reservation.get("branch", "未提供")
    memo = reservation.get("memo", "無")
    user_id = reservation.get("user_id", "unknown")
    draft_id = reservation.get("draft_id", "unknown")
    
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
                { "type": "text", "text": f"時間：{start_time}" },
                { "type": "text", "text": f"分店：{branch}" },
                { "type": "text", "text": f"備註：{memo}" },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "✅ 確認新增",
                        "data": f"action=select_branch&draft_id={draft_id}"
                    },
                    "style": "primary"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "📑 修改",
                        "data": f"action=edit&draft_id={draft_id}"
                    },
                    "style": "secondary"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "❌ 刪除",
                        "data": f"action=delete&draft_id={draft_id}"
                    },
                    "style": "secondary"
                }
            ]
        }
    }

    return FlexSendMessage(alt_text="預約審核通知", contents=flex_json)

# 前一天提醒 NEW
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

def build_branch_selection_flex(draft_id: str) -> FlexSendMessage:
    return FlexSendMessage(
        alt_text="請選擇分店",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": "請選擇分店", "weight": "bold", "size": "lg"},
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "A 分店",
                            "data": f"action=confirm&draft_id={draft_id}&branch=A分店"
                        },
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "B 分店",
                            "data": f"action=confirm&draft_id={draft_id}&branch=B分店"
                        },
                        "style": "primary"
                    }
                ]
            }
        }
    )
