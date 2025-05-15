from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from handlers.unified_router import register_handlers
import os

load_dotenv()
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 註冊 handlers（加上錯誤追蹤）
try:
    # print("🔐 初始化 WebhookHandler，Secret 長度:", len(os.getenv("LINE_CHANNEL_SECRET") or ''))
    register_handlers(handler)
    # print("✅ register_handlers 成功完成")
except Exception as e:
    import traceback
    print("❌ register_handlers 發生錯誤:")
    traceback.print_exc()

print("🧩 正在執行 reservation_bot/app.py")

@app.route("/callback", methods=['POST', 'GET'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    """
    print("🔥 Webhook /callback 被觸發了")
    print("➡️ Headers:", dict(request.headers))
    print("➡️ Method:", request.method)
    print("➡️ Content-Type:", request.content_type)
    print("📦 Body:", body)
    print("🔐 SECRET loaded:", os.getenv("LINE_CHANNEL_SECRET"))
    """
    
    if not signature:
        print("❌ 缺少 X-Line-Signature 標頭")
        abort(400)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ Signature 驗證失敗，請確認 LINE_CHANNEL_SECRET 是否正確")
        abort(403)
    except Exception as e:
        import traceback
        print("❌ 其他處理錯誤:")
        traceback.print_exc()
        abort(500)

    print("✅ 處理成功，回傳 200")
    return 'OK'

#-------------------------------------
# 定時ping的功能，避免render進入休眠狀態
@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.before_request
def catch_all_requests():
    print(f"🛎️ 收到請求：{request.method} {request.path}")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_unknown(path):
    print(f"⚠️ 未知路由被打到了：/{path} ({request.method})")
    return "Unknown route", 404

"""
print("📂 執行目錄:", os.getcwd())
print("🧠 __name__ =", __name__)
print("🔧 已註冊路由:")
for rule in app.url_map.iter_rules():
    print(f"   ↪ {rule}")
"""    

# === Entry point ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)