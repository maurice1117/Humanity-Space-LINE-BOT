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

def notify_reservation_being_check(reservation, checked):

    reservation_type = "預約" if checked else "修改"
    name = reservation.get("name") or "顧客"
    tel = reservation.get("tel") or "未提供"
    date = reservation.get("date") or "未提供"
    memo = reservation.get("memo") or "無"
    start_time = reservation.get("start_time") or "無"
    branch = reservation.get("branch") or "無"

    notify_text_json = {
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "text",
            "text": f'✅ {reservation_type}已確認',
            "weight": "bold",
            "size": "xl"
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
                    "text": "姓名",
                    "color": "#aaaaaa",
                    "size": "md",
                    "flex": 1,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": name,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "text": "電話",
                    "color": "#aaaaaa",
                    "size": "md",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": tel,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "size": "md",
                    "flex": 1,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": date,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "size": "md",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": start_time,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "text": "分店",
                    "color": "#aaaaaa",
                    "size": "md",
                    "flex": 1,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": branch,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "text": "備註",
                    "color": "#aaaaaa",
                    "size": "md",
                    "flex": 1,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": memo,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
                }
                ]
            }
            ]
        }
        ]
    }
    }
    return FlexSendMessage(alt_text="預約已確認", contents=notify_text_json)

def notify_reservation_being_delete(reservation, refuse):

    refuse = "拒絕" if refuse else "刪除"
    name = reservation.get("name", "顧客")
    tel = reservation.get("tel", "未提供")
    date = reservation.get("date", "未提供")
    memo = reservation.get("memo", "無")
    start_time = reservation.get("start_time", "無")
    branch = reservation.get("branch", "無")
    
    notify_text_json = {
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "text",
            "text": f'您的預約已被{refuse}',
            "weight": "bold",
            "size": "xl"
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
                    "text": "姓名",
                    "color": "#aaaaaa",
                    "size": "md",
                    "flex": 1,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": name,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "text": "電話",
                    "color": "#aaaaaa",
                    "size": "md",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": tel,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "size": "md",
                    "flex": 1,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": date,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "size": "md",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": start_time,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "text": "分店",
                    "color": "#aaaaaa",
                    "size": "md",
                    "flex": 1,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": branch,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
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
                    "text": "備註",
                    "color": "#aaaaaa",
                    "size": "md",
                    "flex": 1,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": memo,
                    "wrap": True,
                    "color": "#666666",
                    "size": "md",
                    "flex": 5
                }
                ]
            }
            ]
        }
        ]
    }
    }
    return FlexSendMessage(alt_text="預約已確認", contents=notify_text_json)

def build_delete_confirm_flex(reservation):
    
    name = reservation.get("name", "顧客")
    tel = reservation.get("tel", "未提供")
    date = reservation.get("date", "未提供")
    memo = reservation.get("memo", "無")
    start_time = reservation.get("start_time", "無")
    branch = reservation.get("branch", "無")
    draft_id = reservation.get("draft_id", "0")
    flex_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"確定是否刪除該預約",
                    "weight": "bold",
                    "size": "xl"
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
                                {"type": "text", "text": "姓名", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": name, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "電話", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": tel, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "日期", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": date, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "時間", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": start_time, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "分店", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": branch, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "備註", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": memo, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#DD0000",
                    "action": {
                        "type": "postback",
                        "label": "✅ 確定刪除",
                        "data": f"action=confirm_delete&id={draft_id}"
                    }
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "取消",
                        "text": "已取消刪除"
                    }
                }
            ]
        }
    }

    return flex_json

def build_delete_reservation_flex(reservation):
    

    name = reservation.get("name") or "顧客"
    tel = reservation.get("tel") or "未提供"
    date = reservation.get("date") or "未提供"
    memo = reservation.get("memo") or "無"
    start_time = reservation.get("start_time") or "無"
    branch = reservation.get("branch") or "無"
    uid = reservation.get("uid", "0")
        
    flex_json = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"確定是否刪除該預約",
                    "weight": "bold",
                    "size": "xl"
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
                                {"type": "text", "text": "姓名", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": name, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "電話", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": tel, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "日期", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": date, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "時間", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": start_time, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "分店", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": branch, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {"type": "text", "text": "備註", "color": "#aaaaaa", "size": "md", "flex": 1},
                                {"type": "text", "text": memo, "wrap": True, "color": "#666666", "size": "md", "flex": 5}
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#DD0000",
                    "action": {
                        "type": "postback",
                        "label": "✅ 確定刪除",
                        "data": f"action=confirm_delete&id={uid}"
                    }
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "取消",
                        "text": "已取消刪除"
                    }
                }
            ]
        }
    }

    return flex_json