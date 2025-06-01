from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from handlers.unified_router import register_handlers
from services.notify_text import daily_evening_notify, hourly_check_notify
from datetime import datetime
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

# -------------------------------------
@app.route("/test/daily-notify", methods=["GET"])
def test_daily_notify():
    try:
        print("🧪 開始測試每日晚間通知...")
        success_count = daily_evening_notify()
        
        result = {
            "status": "success",
            "message": "每日晚間通知測試完成",
            "notifications_sent": success_count,
            "timestamp": str(datetime.now())
        }
        
        print(f"✅ 測試完成: {result}")
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        error_msg = f"每日通知測試失敗: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": error_msg,
            "timestamp": str(datetime.now())
        }), 500


@app.route("/test/hour-notify", methods=["GET"])
def test_hour_notify():
    try:
        print("🧪 開始測試小時通知...")
        success_count = hourly_check_notify()
        
        result = {
            "status": "success",
            "message": "小時通知測試完成",
            "notifications_sent": success_count,
            "timestamp": str(datetime.now())
        }
        
        print(f"✅ 測試完成: {result}")
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        error_msg = f"小時通知測試失敗: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": error_msg,
            "timestamp": str(datetime.now())
        }), 500
    
# === Entry point ===
port = int(os.getenv("PORT", 5000))  # 默認使用 5000 埠
app.run(host="0.0.0.0", port=port, debug=True)
