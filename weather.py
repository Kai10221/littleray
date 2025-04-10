import os
import requests
from linebot.models import FlexSendMessage, TextSendMessage

def get_current_weather(city):
    """
    呼叫 WeatherAPI.com 的 Current Weather API 取得目前天氣資料，
    回傳字典格式如下：
      {
         "city": 城市名稱,
         "temp": 溫度 (攝氏),
         "condition": 天氣描述,
         "icon": 天氣圖示的完整 URL,
         "humidity": 濕度,
         "wind_speed": 風速 (公里/時),
         "city_id": 城市代碼  (不一定需要)
      }
    """
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return None
    base_url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "lang": "zh"  # 使用中文
    }
    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()
        if "error" in data:
            return None
        # WeatherAPI 回傳的 condition.icon 通常是以 "//cdn.weatherapi.com/..."，需要補上 https:
        icon_url = data["current"]["condition"]["icon"]
        if icon_url.startswith("//"):
            icon_url = "https:" + icon_url

        return {
            "city": data["location"]["name"],
            "temp": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "icon": icon_url,
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph"],
            "city_id": data["location"]["id"] if "id" in data["location"] else ""
        }
    except Exception:
        return None

def make_weather_carousel(weather):
    """
    根據取得的天氣資訊，組成 Flex Message Carousel，
    包含兩個 Bubble：
      - 第一則：顯示「今天 {城市} 天氣」詳細資訊
      - 第二則：顯示「一週 {城市} 天氣」，按鈕點擊後導向 Google 搜尋查詢該城市天氣
    若無天氣資料，回傳 TextSendMessage。
    """
    if not weather:
        return TextSendMessage(text="無法取得天氣資料")

    # 利用 WeatherAPI 提供的天氣圖示作為主圖
    icon_url = weather["icon"]

    bubble_today = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": icon_url,
            "size": "full",
            "aspectRatio": "1:1",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"今天 {weather['city']} 天氣",
                    "weight": "bold",
                    "size": "lg",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": weather["condition"],
                    "size": "md",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": f"溫度：{weather['temp']}°C",
                    "size": "sm",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": f"濕度：{weather['humidity']}%",
                    "size": "sm",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": f"風速：{weather['wind_speed']} km/h",
                    "size": "sm",
                    "wrap": True
                }
            ]
        }
    }

    # 以 Google 搜尋作為一週天氣查詢頁面的連結
    bubble_week = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": icon_url,
            "size": "full",
            "aspectRatio": "1:1",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"一週 {weather['city']} 天氣",
                    "weight": "bold",
                    "size": "lg",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "點擊查看詳細預報",
                    "size": "md",
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
                    "style": "primary",
                    "action": {
                        "type": "uri",
                        "label": "一週天氣",
                        # 使用 Google 搜尋天氣作為連結，方便使用者查看多日預報
                        "uri": f"https://www.google.com/search?q={weather['city']}+天氣"
                    }
                }
            ]
        }
    }

    carousel = {
        "type": "carousel",
        "contents": [bubble_today, bubble_week]
    }

    return FlexSendMessage(alt_text=f"{weather['city']} 天氣資訊", contents=carousel)

def handle_weather(event, line_bot_api):
    """
    根據使用者輸入的訊息取得城市名稱 (例如「台北天氣」)，
    呼叫 get_current_weather() 取得天氣資訊，
    並使用 make_weather_carousel() 組成 Flex Message 回覆使用者。
    """
    text = event.message.text.strip()
    if text.endswith("天氣"):
        city = text[:-2]
    else:
        city = text
    weather = get_current_weather(city)
    msg = make_weather_carousel(weather)
    line_bot_api.reply_message(event.reply_token, msg)
