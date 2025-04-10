import os
import requests
from linebot.models import FlexSendMessage, TextSendMessage

def get_current_weather(city):
    """
    呼叫 OpenWeatherMap API 取得目前天氣資料，回傳一個字典，格式：
      {
         "city": 城市名稱,
         "description": 天氣描述,
         "temp": 溫度,
         "humidity": 濕度,
         "wind_speed": 風速,
         "icon": 天氣 icon 代碼,
         "city_id": 城市代號
      }
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",   # 攝氏溫度
        "lang": "zh_tw"        # 語言設定為中文繁體
    }
    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()
        if data.get("cod") != 200:
            return None
        return {
            "city": data.get("name", city),
            "description": data["weather"][0]["description"],
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "icon": data["weather"][0]["icon"],
            "city_id": data["id"]
        }
    except Exception:
        return None

def make_weather_carousel(weather):
    """
    根據取得的天氣資訊，組成 Flex Message 的 Carousel 格式，
    包含兩個 Bubble：
      - 第1則：顯示「今天 xxx 的天氣」，呈現詳細資訊
      - 第2則：顯示「一週 xxx 的天氣」，並提供按鈕連結到詳細預報網頁
    若無天氣資料，回傳一則文字訊息。
    """
    if not weather:
        return TextSendMessage(text="無法取得天氣資料")
    
    # OpenWeatherMap 提供 icon 圖示的 URL，格式為 https://openweathermap.org/img/wn/{icon}@2x.png
    icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png"
    
    # Bubble 1：今天的天氣
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
                    "text": f"今天{weather['city']}的天氣",
                    "weight": "bold",
                    "size": "lg",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": weather["description"],
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
                    "text": f"風速：{weather['wind_speed']} m/s",
                    "size": "sm",
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
                        "label": "詳細資訊",
                        "uri": f"https://openweathermap.org/city/{weather['city_id']}"
                    }
                }
            ]
        }
    }
    
    # Bubble 2：一週天氣（這裡以相同的城市預報連結為例）
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
                    "text": f"一週{weather['city']}的天氣",
                    "weight": "bold",
                    "size": "lg",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "點擊查看未來天氣趨勢",
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
                        "uri": f"https://openweathermap.org/city/{weather['city_id']}"
                    }
                }
            ]
        }
    }
    
    carousel = {
        "type": "carousel",
        "contents": [bubble_today, bubble_week]
    }
    
    return FlexSendMessage(alt_text=f"{weather['city']}天氣資訊", contents=carousel)

def handle_weather(event, line_bot_api):
    """
    根據使用者訊息（例如「台北天氣」或「高雄天氣」），
    取得天氣資訊並回覆一則 Flex Message 卡片。
    """
    text = event.message.text.strip()
    # 假設訊息格式為「城市名稱+天氣」，例如「台北天氣」
    if text.endswith("天氣"):
        city = text[:-2]
    else:
        city = text
    weather = get_current_weather(city)
    flex_msg = make_weather_carousel(weather)
    line_bot_api.reply_message(event.reply_token, flex_msg)
