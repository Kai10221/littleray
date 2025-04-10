import requests
import random
from bs4 import BeautifulSoup
from linebot.models import FlexSendMessage, TextSendMessage

def get_hot_articles():
    """
    從 disp.cc 熱門文章列表取得資料，並隨機抽取 5 篇文章。
    每篇文章資料格式：
        {"title": <文章標題>, "link": <文章連結>}
    """
    url = "https://disp.cc/b/"
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        # 根據 disp.cc 的頁面結構，篩選出以 https://disp.cc/b/ 開頭的連結，且文字不為空
        for a in soup.find_all("a"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            if href.startswith("https://disp.cc/b/") and text:
                articles.append({"title": text, "link": href})
        if len(articles) >= 5:
            return random.sample(articles, 5)
        else:
            return articles
    except Exception as e:
        return []

def make_flex_carousel(articles):
    """
    將取得的文章資料轉換成 LINE Flex Message 的 Carousel 格式，
    每個 Bubble 顯示文章標題與一個按鈕，點擊後可直接開啟原文連結。
    
    若文章資料為空，則回傳一個簡單的文字訊息。
    """
    if not articles:
        return TextSendMessage(text="目前沒有熱門文章")
    
    bubbles = []
    for article in articles:
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": article["title"],
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "看文章",
                            "uri": article["link"]
                        }
                    }
                ]
            }
        }
        bubbles.append(bubble)
    
    carousel = {
        "type": "carousel",
        "contents": bubbles
    }
    
    return FlexSendMessage(alt_text="熱門推文", contents=carousel)
