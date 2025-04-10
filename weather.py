import os
import requests
from linebot.models import FlexSendMessage, TextSendMessage

def get_current_weather(city):
    """
    呼叫 WeatherAPI.com 的 Current Weather API 取得目前天氣資料，回傳一個字典，格式：
      {
         "city": 城市名稱,
         "temp": 溫度 (°C),
         "condition": 天氣描述,
         "icon": 天氣圖示 URL,
         "humidity": 濕度,
         "wind_speed": 風速 (km/h),
         "city_id": 城市代碼（可能為空）
      }
    """
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return None
    base_url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "lang": "zh"
    }
    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()
        if "error" in data:
            return None
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
            "city_id": data["location"].get("id", "")  # 此欄位可能為空
        }
    except Exception:
        return None

def make_weather_carousel(weather):
    """
    根據天氣資訊，組成 Flex Message 的 Carousel 格式，
    包含兩個 Bubble：
      - 第一則：顯示「今天 {城市} 天氣」詳細資訊
      - 第二則：顯示「一週 {城市} 天氣」，按鈕導向至 Google 搜尋該城市天氣
    若無天氣資料，回傳 TextSendMessage。
    """
    if not weather:
        return TextSendMessage(text="無法取得天氣資料")
    
    icon_url = weather["icon"]
    # 如果 city_id 為空，則使用 Google 搜尋作為詳細資訊頁面
    if weather["city_id"]:
        detailed_uri = f"https://openweathermap.org/city/{weather['city_id']}"
    else:
        detailed_uri = f"https://www.google.com/search?q={weather['city']}+天氣"
    
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
                    "text": f"今天 {weather['city']} 的天氣",
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
                        "uri": detailed_uri
                    }
                }
            ]
        }
    }
    
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
                    "text": f"一週 {weather['city']} 的天氣",
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
    根據使用者訊息（例如「台北天氣」）取得城市名稱，
    查詢天氣後回覆一則 Flex Message 卡片。
    """
    text = event.message.text.strip()
    if text.endswith("天氣"):
        city = text[:-2]
    else:
        city = text
    weather = get_current_weather(city)
    msg = make_weather_carousel(weather)
    line_bot_api.reply_message(event.reply_token, msg)
