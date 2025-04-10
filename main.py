from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage

import os

# 匯入各功能模組
from pttbeauty import handle_beauty
from ptt_hot import get_hot_articles, make_flex_carousel

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
    text = event.message.text

    # 功能 1：抽圖（轉交給 pttbeauty 模組處理）
    if "抽" in text:
        handle_beauty(event, line_bot_api)

    # 功能 2：PTT 熱門文章
    elif any(kw in text for kw in ["熱門", "推文", "排行"]):
        articles = get_hot_articles()
        flex_msg = make_flex_carousel(articles)
        line_bot_api.reply_message(event.reply_token, flex_msg)

    # 其他訊息回覆
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text="你說了：" + text)
        )

