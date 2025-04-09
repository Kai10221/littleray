from flask import Flask, request, abort
from bs4 import BeautifulSoup
import requests, random, os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, ImageSendMessage, TextSendMessage

main = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@main.route("/")
def home():
    return "Line Bot Running"

@main.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Webhook 處理錯誤：", e)
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text.strip() == "抽圖":
        image_url = get_random_beauty_image()
        print("抓到的圖片網址：", image_url)  # debug log
        if image_url:
            msg = ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url
            )
            line_bot_api.reply_message(event.reply_token, msg)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="沒抓到圖片，稍後再試～")
            )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你說了：" + event.message.text)
        )

def get_random_beauty_image():
    base_url = "https://www.ptt.cc"
    index_url = base_url + "/bbs/Beauty/index.html"
    rs = requests.get(index_url, headers={"cookie": "over18=1"})
    soup = BeautifulSoup(rs.text, "html.parser")

    links = [base_url + a["href"] for a in soup.select(".r-ent a") if a]
    random.shuffle(links)

    for link in links:
        res = requests.get(link, headers={"cookie": "over18=1"})
        s = BeautifulSoup(res.text, "html.parser")
        imgs = []
        for a in s.select("a"):
            href = a.get("href", "")
            if "imgur.com" in href:
                if href.startswith("https://imgur.com"):
                    href = href.replace("https://imgur.com", "https://i.imgur.com") + ".jpg"
                if href.startswith("http"):
                    imgs.append(href)
        if imgs:
            return random.choice(imgs)

    return None
