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

# 註冊 handlers
try:
    register_handlers(handler)
except Exception as e:
    import traceback
    print("❌ register_handlers 發生錯誤:")
    traceback.print_exc()

print("🧩 正在執行 reservation_bot/app.py")

@app.route("/callback", methods=['POST', 'GET'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    
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


# === Entry point ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)