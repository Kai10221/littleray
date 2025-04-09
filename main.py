from flask import Flask, request, abort
from bs4 import BeautifulSoup
import requests, random, os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, ImageSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("ouqCgkXOXiP5+pPOFoJPQqUXBB0j6aVUtCOl6RQRt/LW6qIjbrSSOwHL3qMx0jfuYux0vfpmo/EE1KDtXE+8uqfIJV4fDCJyc9/MLCdl4OqyBJnTweG6xWvn7om2+8MVJKHBFVvM2bQBzQG67PAhuwdB04t89/1O/w1cDnyilFU="))
handler = WebhookHandler(os.getenv("ca60feb7c097c5295d0f2d4b2791a05a"))

@app.route("/")
def home():
    return "Line Bot Running"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "抽圖":
        image_url = get_random_beauty_image()
        if image_url:
            msg = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
            line_bot_api.reply_message(event.reply_token, msg)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒抓到圖片，再試一次！"))

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
        imgs = [img["href"] for img in s.select("a") if "imgur.com" in img.get("href", "")]
        if imgs:
            return random.choice(imgs)

    return None
