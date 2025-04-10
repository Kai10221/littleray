# ptt_hot.py
import requests
import random
from bs4 import BeautifulSoup

def get_hot_articles():
    """
    從 disp.cc 的熱門列表取得文章資料，
    回傳隨機抽取的 5 篇熱門文章（若不足 5 篇就全部回傳）。
    每篇文章的資料是一個 dict，格式:
        {"title": 標題, "link": 文章連結}
    """
    url = "https://disp.cc/b/"
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        # 根據 disp.cc 的頁面結構，找出所有連結（這裡以所有 <a> 標籤作篩選）
        for a in soup.find_all("a"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            # 過濾出網址以 "https://disp.cc/b/" 開頭的文章連結，且標題不空
            if href.startswith("https://disp.cc/b/") and text:
                articles.append({"title": text, "link": href})
        if len(articles) >= 5:
            return random.sample(articles, 5)
        else:
            return articles
    except Exception as e:
        # 若發生錯誤則回傳空列表
        return []

def make_flex_carousel(articles):
    """
    將文章資料轉換成 LINE Flex Message 的 carousel 格式，
    每個 Bubble 顯示文章標題以及一個按鈕連結。
    若文章資料為空，則回傳一個簡單的 TextSendMessage（需由 linebot.models.TextSendMessage 處理）。
    """
    if not articles:
        from linebot.models import TextSendMessage
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
    
    flex_message = {
        "type": "flex",
        "altText": "熱門推文",
        "contents": {
            "type": "carousel",
            "contents": bubbles
        }
    }
    
    return flex_message
