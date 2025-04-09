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
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    if "抽" in user_message:  # ✅ 判斷只要包含「抽」
        image_url = get_random_beauty_image()
        print("抓到的圖片網址：", image_url)
        if image_url:
            msg = ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url
            )
            line_bot_api.reply_message(event.reply_token, msg)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="目前沒抓到圖片，再試一次！")
            )
    else:
        # 非抽圖文字的回應
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你說了：" + user_message)
        )


def get_random_beauty_image():
    base_url = "https://www.ptt.cc"
    index_urls = [
        base_url + "/bbs/Beauty/index.html",
        base_url + "/bbs/Beauty/index{}.html".format(i) for i in range(1, 3)
    ]
    
    article_links = []

    # 抓取多頁文章連結
    for url in index_urls:
        rs = requests.get(url, headers={"cookie": "over18=1"})
        soup = BeautifulSoup(rs.text, "html.parser")
        links = [base_url + a["href"] for a in soup.select(".r-ent a") if a]
        article_links.extend(links)

    random.shuffle(article_links)

    for link in article_links:
        try:
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
            print("👉 正在檢查文章：", link)
            print("🎯 圖片列表：", imgs)
            if imgs:
                return random.choice(imgs)
        except Exception as e:
            print("❗ 抓取文章錯誤：", link, e)
            continue

    return None

