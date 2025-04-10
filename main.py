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
    except Exception as e:
        print("Webhook 處理錯誤:", e)
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 記錄收到的訊息
    print("收到訊息:", event.message.text)
    # 只要訊息中有 "抽" 就觸發回傳圖片功能
    if "抽" in event.message.text:
        image_url = get_random_beauty_image()
        print("抓到的圖片網址:", image_url)
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
    # 合併固定首頁與其他頁面：用方法1
    index_urls = [base_url + "/bbs/Beauty/index.html"] + [base_url + "/bbs/Beauty/index{}.html".format(i) for i in range(1, 3)]
    article_links = []
    for url in index_urls:
        try:
            rs = requests.get(url, headers={"cookie": "over18=1"}, timeout=5)
            soup = BeautifulSoup(rs.text, "html.parser")
            links = [base_url + a["href"] for a in soup.select(".r-ent a") if a.get("href")]
            article_links.extend(links)
        except Exception as e:
            print("取得文章連結失敗:", url, e)
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
            print("檢查文章:", link, "圖列表:", imgs)
            if imgs:
                return random.choice(imgs)
        except Exception as e:
            print("抓取文章失敗:", link, e)
            continue
    return None
