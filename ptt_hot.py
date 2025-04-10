import requests
import random
from bs4 import BeautifulSoup
from linebot.models import FlexSendMessage, TextSendMessage

def get_hot_articles():
    """
    從 disp.cc 的熱門文章列表取得資料，擷取文章標題、文章連結，
    並嘗試抓取文章內的第一個圖片 (若有)。
    回傳 5 篇隨機熱門文章，每筆資料格式:
        {"title": <標題>, "link": <連結>, "image": <圖片網址或空字串>}
    """
    url = "https://disp.cc/b/"
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        for a in soup.find_all("a"):
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if href.startswith("https://disp.cc/b/") and title:
                article = {"title": title, "link": href, "image": ""}
                # 嘗試抓取文章內第一個圖片網址
                try:
                    art_resp = requests.get(href, timeout=5)
                    art_soup = BeautifulSoup(art_resp.text, "html.parser")
                    img_tag = art_soup.find("img")
                    if img_tag:
                        img_url = img_tag.get("src", "")
                        if img_url.startswith("http://"):
                            img_url = img_url.replace("http://", "https://")
                        if img_url.startswith("https://"):
                            article["image"] = img_url
                except Exception:
                    pass
                articles.append(article)
        if len(articles) >= 5:
            return random.sample(articles, 5)
        else:
            return articles
    except Exception:
        return []

def make_flex_carousel(articles):
    """
    將熱門文章資料轉換成美化版的 Flex Message Carousel 物件。
    若每筆資料有內文圖片，Hero 區會顯示該圖片，否則使用預設圖片。
    """
    if not articles:
        return TextSendMessage(text="目前沒有熱門文章")
    
    default_image = "https://i.imgur.com/H2fNoTr.jpg"  # 請依需要更換成你喜歡的預設圖片
    bubbles = []
    for article in articles:
        hero_image = article["image"] if article["image"] else default_image
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": hero_image,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": article["title"],
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "熱門推文",
                        "size": "sm",
                        "color": "#999999",
                        "wrap": True,
                        "margin": "md"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#1DB446",
                        "action": {
                            "type": "uri",
                            "label": "閱讀全文",
                            "uri": article["link"]
                        }
                    }
                ]
            },
            "styles": {
                "hero": {
                    "separator": True
                },
                "footer": {
                    "separator": True
                }
            }
        }
        bubbles.append(bubble)
    
    carousel = {
        "type": "carousel",
        "contents": bubbles
    }
    
    return FlexSendMessage(alt_text="熱門推文", contents=carousel)
