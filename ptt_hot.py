# ptt_hot.py
import requests
import random
from bs4 import BeautifulSoup
from linebot.models import FlexSendMessage

def get_hot_articles():
    url = "https://disp.cc/b/"
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    articles = []

    for row in soup.select("div.row2")[:30]:  # 抓前 30 篇以內隨機抽
        try:
            title_tag = row.select_one("span.listTitle")
            if not title_tag:
                continue

            title = title_tag.text.strip()
            href = "https://disp.cc" + title_tag.a["href"]
            author = row.select_one("span.author").text.strip()
            push = row.select_one("span.listPush").text.strip()

            articles.append({
                "title": title,
                "url": href,
                "author": author,
                "push": push
            })
        except:
            continue

    return random.sample(articles, 5) if len(articles) >= 5 else articles

def make_flex_carousel(articles):
    bubbles = []

    for article in articles:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {"type": "text", "text": article["title"], "wrap": True, "weight": "bold", "size": "md"},
                    {"type": "text", "text": f"作者：{article['author']}", "size": "sm", "color": "#888888"},
                    {"type": "text", "text": f"推文：{article['push']}", "size": "sm", "color": "#888888"}
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
                            "label": "🔗 點我看原文",
                            "uri": article["url"]
                        },
                        "style": "primary",
                        "color": "#1DB446"
                    }
                ]
            }
        }
        bubbles.append(bubble)

    return FlexSendMessage(
        alt_text="PTT 熱門文章排行",
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )
