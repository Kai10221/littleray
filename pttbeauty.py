from bs4 import BeautifulSoup
import requests, random
from linebot.models import ImageSendMessage, TextSendMessage

def handle_beauty(event, line_bot_api):
    image_url = get_random_beauty_image()
    # 如果圖片連結不以 "https://" 開頭，則直接回覆文字（或你也可進行其他錯誤處理）
    if image_url and image_url.startswith("https://"):
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
    # 取得 Beauty 版首頁與其他兩頁
    index_urls = [base_url + "/bbs/Beauty/index.html"] + \
                 [base_url + "/bbs/Beauty/index{}.html".format(i) for i in range(1, 3)]
    article_links = []
    for url in index_urls:
        try:
            rs = requests.get(url, headers={"cookie": "over18=1"}, timeout=5)
            soup = BeautifulSoup(rs.text, "html.parser")
            # 收集所有文章的連結
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
                    # 如果網址以 "https://imgur.com" 開頭，轉成 "https://i.imgur.com" 加上副檔名
                    if href.startswith("https://imgur.com"):
                        href = href.replace("https://imgur.com", "https://i.imgur.com") + ".jpg"
                    # 如果網址是以 "http://" 開頭，變成 https
                    elif href.startswith("http://"):
                        href = href.replace("http://", "https://")
                    # 確保網址以 "https://" 開頭
                    if href.startswith("https://"):
                        imgs.append(href)
            if imgs:
                return random.choice(imgs)
        except:
            continue
    return None
