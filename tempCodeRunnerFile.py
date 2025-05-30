## test
# @app.route("/manual_notify")
# def manual_notify():
#     notify_type = request.args.get("type", "daily")
#     if notify_type == "daily":
#         count = daily_evening_notify()
#         return f"✅ 已執行 daily_evening_notify，共發送 {count} 條訊息", 200
#     elif notify_type == "hourly":
#         count = hourly_check_notify()
#         return f"✅ 已執行 hourly_check_notify，共發送 {count} 條訊息", 200
#     else:
#         return "❌ 請指定 type=daily 或 type=hourly", 400
    