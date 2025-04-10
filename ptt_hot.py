import requests
import random
from bs4 import BeautifulSoup

def get_hot_articles():
    """
    從 disp.cc 熱門文章列表取得資料，隨機選取 5 篇文章。
    每筆資料格式包含 "title"、"link" 與 "image"（若內文有圖片）。
    """
    url = "https://disp.cc/b/"
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        # 篩選出所有連結（這邊假設連結前綴為 https://disp.cc/b/）
        for a in soup.find_all("a"):
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if href.startswith("https://disp.cc/b/") and title:
                # 建立初步資料
                article = {"title": title, "link": href, "image": ""}
                # 嘗試進一步抓取文章內容中的第一個圖片
                try:
                    art_resp = requests.get(href, timeout=5)
                    art_soup = BeautifulSoup(art_resp.text, "html.parser")
                    img_tag = art_soup.find("img")
                    if img_tag:
                        img_url = img_tag.get("src", "")
                        # 確保圖片網址以 https:// 開頭，若不是則轉換或略過
                        if img_url.startswith("http://"):
                            img_url = img_url.replace("http://", "https://")
                        if img_url.startswith("https://"):
                            article["image"] = img_url
                    # 若找不到圖片，就 article["image"] 會保持為空字串
                except Exception:
                    # 發生錯誤時，不影響其他資料擷取
                    pass

                articles.append(article)
        if len(articles) >= 5:
            return random.sample(articles, 5)
        else:
            return articles
    except Exception as e:
        return []

from linebot.models import FlexSendMessage, TextSendMessage

def make_flex_carousel(articles):
    """
    根據文章資料建立 Flex Carousel。若每筆文章有 "image" 欄位且不為空，則使用該圖片；否則使用預設圖片。
    """
    if not articles:
        return TextSendMessage(text="目前沒有熱門文章")
    
    default_image = "https://i.imgur.com/H2fNoTr.jpg"  # 預設圖片
    
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
                        "size": "md",
                        "wrap": True
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "來源：disp.cc",
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
                        "margin": "md"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#00BB00",
                        "action": {
                            "type": "uri",
                            "label": "看文章",
                            "uri": article["link"]
                        }
                    }
                ]
            },
            "styles": {
                "hero": {
                    "backgroundColor": "#DDDDDD"
                },
                "body": {
                    "backgroundColor": "#FFFFFF"
                },
                "footer": {
                    "backgroundColor": "#F2F2F2"
                }
            }
        }
        bubbles.append(bubble)
    
    carousel = {
        "type": "carousel",
        "contents": bubbles
    }
    return FlexSendMessage(alt_text="熱門推文", contents=carousel)
