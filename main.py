from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage

import os

# 匯入各功能模組
from pttbeauty import handle_beauty
from ptt_hot import get_hot_articles, make_flex_carousel
from weather import handle_weather

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/")
def home():
    return "Line Bot Running"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("LINE Webhook 發生錯誤：", e)
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()

    # 功能 1：抽圖（交由 pttbeauty 模組處理）
    if "抽" in text:
        handle_beauty(event, line_bot_api)

    # 功能 2：PTT 熱門文章
    elif any(kw in text for kw in ["熱門", "推文", "排行"]):
        articles = get_hot_articles()
        flex_msg = make_flex_carousel(articles)
        line_bot_api.reply_message(event.reply_token, flex_msg)

    # 功能 3：天氣查詢（輸入例如「台北天氣」）
    elif text.endswith("天氣"):
        from weather import handle_weather  # 請先在 weather.py 中定義 handle_weather
        handle_weather(event, line_bot_api)

    # 其他訊息回覆
    else:
       pass
