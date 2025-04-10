from linebot.models import FlexSendMessage, TextSendMessage

def make_flex_carousel(articles):
    """
    美化版：使用 Hero + Body + Footer + styles 來做更好看的 Carousel。
    如果沒有文章，回傳文字訊息。
    """
    if not articles:
        return TextSendMessage(text="目前沒有熱門文章")
    
    # 可以自訂一張預設 Hero 圖
    placeholder_image = "https://i.imgur.com/H2fNoTr.jpg"

    bubbles = []
    for article in articles:
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": placeholder_image,
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
                        "text": "文章來源：disp.cc",
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
