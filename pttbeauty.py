from bs4 import BeautifulSoup
import requests, random
from linebot.models import ImageSendMessage, TextSendMessage

def handle_beauty(event, line_bot_api):
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
    # 抓取 Beauty 版文章，依序來自首頁與其他 2 頁
    index_urls = [base_url + "/bbs/Beauty/index.html"] + \
                 [base_url + "/bbs/Beauty/index{}.html".format(i) for i in range(1, 10)]
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
