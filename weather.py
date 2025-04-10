import os
import requests
import urllib.parse
from linebot.models import FlexSendMessage, TextSendMessage

# 台灣主要城市中英對照（可根據需要擴充）
CITY_MAPPING = {
    "台北": "Taipei",
    "新北": "New Taipei",
    "桃園": "Taoyuan",
    "台中": "Taichung",
    "台南": "Tainan",
    "高雄": "Kaohsiung",
    "基隆": "Keelung",
    "新竹": "Hsinchu",
    "嘉義": "Chiayi",
    "宜蘭": "Yilan",
    "苗栗": "Miaoli",
    "彰化": "Changhua",
    "南投": "Nantou",
    "雲林": "Yunlin",
    "屏東": "Pingtung",
    "花蓮": "Hualien",
    "台東": "Taitung",
    "澎湖": "Penghu",
    "金門": "Kinmen",
    "馬祖": "Matsu"
}

def get_current_weather(city):
    """
    呼叫 OpenWeatherMap API 取得目前天氣資料，回傳字典格式：
      {
         "city": 城市名稱,
         "temp": 溫度 (°C),
         "condition": 天氣描述,
         "icon": 天氣圖示 URL,
         "humidity": 濕度,
         "wind_speed": 風速 (m/s),
         "city_id": 城市代碼
      }
    """
    # 如果使用者輸入的是中文城市名稱，嘗試轉換成英文
    if city in CITY_MAPPING:
        city = CITY_MAPPING[city]
    api_key = os.getenv("OPENWEATHERMAP_KEY")
    if not api_key:
        return None
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",   # 使用攝氏
        "lang": "zh_tw"      # 回傳中文描述
    }
    try:
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()
        if data.get("cod") != 200:
            return None
        # 取得圖示代碼，OpenWeatherMap 提供的天氣圖示 URL 格式：
        # https://openweathermap.org/img/wn/{icon}@2x.png
        icon_code = data["weather"][0]["icon"]
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        return {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "condition": data["weather"][0]["description"],
            "icon": icon_url,
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "city_id": str(data.get("id", ""))
        }
    except Exception:
        return None

def make_weather_carousel(weather):
    """
    根據天氣資訊組成 Flex Message 的 Carousel 格式，
    產生兩個 Bubble：
      - 第一則顯示「今天 {城市} 天氣」詳細資訊
      - 第二則顯示「一週 {城市} 天氣」及查詢按鈕（連結以 Google 搜尋結果為例）
    若無資料則回傳文字訊息。
    """
    if not weather:
        return TextSendMessage(text="無法取得天氣資料")
    
    icon_url = weather["icon"]
    
    if weather["city_id"]:
        detailed_uri = f"https://openweathermap.org/city/{weather['city_id']}"
    else:
        query = f"{weather['city']} 天氣"
        encoded_query = urllib.parse.quote(query)
        detailed_uri = f"https://www.google.com/search?q={encoded_query}"
    
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
                        "uri": f"https://www.google.com/search?q={urllib.parse.quote(weather['city'] + ' 天氣')}"
                    }
                }
            ]
        }
    }
    
    carousel = {
        "type": "carousel",
        "contents": [bubble_today, bubble_week]
    }
    
    return FlexSendMessage(alt_text=f"{weather['city']} 天_
