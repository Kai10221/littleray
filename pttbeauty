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
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if "抽" in event.message.text:
        image_url = get_random_beauty_image()
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

def get_random_beauty_image():
    base_url = "https://www.ptt.cc"
    index_urls = [base_url + "/bbs/Beauty/index.html"] + [base_url + "/bbs/Beauty/index{}.html".format(i) for i in range(1, 3)]
    article_links = []
    for url in index_urls:
        try:
            rs = requests.get(url, headers={"cookie": "over18=1"}, timeout=5)
            soup = BeautifulSoup(rs.text, "html.parser")
            links = [base_url + a["href"] for a in soup.select(".r-ent a") if a.get("href")]
            article_links.extend(links)
        except:
            continue
    random.shuffle(article_links)
    
    for link in article_links:
        try:
            res = requests.get(link, headers={"cookie": "over18=1"}, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            imgs = []
            for a in soup.select("a"):
                href = a.get("href", "")
                if "imgur.com" in href:
                    if href.startswith("https://imgur.com"):
                        href = href.replace("https://imgur.com", "https://i.imgur.com") + ".jpg"
                    if href.startswith("http"):
                        imgs.append(href)
            if imgs:
                return random.choice(imgs)
        except:
            continue
    return None
