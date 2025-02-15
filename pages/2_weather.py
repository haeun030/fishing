# weather_tide.py
import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
from urllib.parse import quote_plus

class WeatherTideAPI:
    def __init__(self):
        self.weather_api_key = quote_plus("afsQnO7BX9vJr+gVZwRPSRxEt85mQOnTti47d8jgPTl27Y1xkkuD+8ETp6+7r/WFaTNio4csNxCrGaZAqHASXQ==")
        self.tide_api_key = "w4xwxxWajdufhWDaudYGrQ=="
    
    def get_base_time(self):
        now = datetime.now()
        if now.minute < 40:
            now = now - timedelta(hours=1)
        return now.strftime("%H00")

    def get_weather(self, nx, ny):
        try:
            base_date = datetime.now().strftime("%Y%m%d")
            base_time = self.get_base_time()
            
            url = f'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?serviceKey={self.weather_api_key}&numOfRows=10&pageNo=1&dataType=JSON&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}'
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'body' in data['response'] and 'items' in data['response']['body']:
                    items = data['response']['body']['items']['item']
                    weather_data = {}
                    
                    for item in items:
                        category = item['category']
                        if category == 'T1H':    # 기온
                            weather_data['temperature'] = float(item['obsrValue'])
                        elif category == 'REH':   # 습도
                            weather_data['humidity'] = float(item['obsrValue'])
                        elif category == 'RN1':   # 1시간 강수량
                            weather_data['rainfall'] = float(item['obsrValue'])
                        elif category == 'WSD':   # 풍속
                            weather_data['wind_speed'] = float(item['obsrValue'])
                    
                    return weather_data
            return None
        except Exception as e:
            st.error(f"날씨 정보 조회 중 오류 발생: {str(e)}")
            return None

    def get_tide(self, obs_code):
    #"""조석 예보 조회"""
        try:
            url = "http://www.khoa.go.kr/api/oceangrid/tideObsPre/search.do"
            today = datetime.now().strftime("%Y%m%d")
            
            params = {
                'ServiceKey': self.tide_api_key,
                'ObsCode': obs_code,
                'Date': today,
                'ResultType': 'json'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'data' in data['result']:
                    tide_data = []
                    for item in data['result']['data']:
                        tide_data.append({
                            'time': item['record_time'].split()[1],  # "2025-02-15 00:00:00" 에서 시간만 추출
                            'tide_level': float(item['tide_level']) / 10  # cm를 m로 변환
                        })
                    return pd.DataFrame(tide_data)
            return None
        except Exception as e:
            st.error(f"조석 정보 조회 중 오류 발생: {str(e)}")
            return None


st.title("🌊 제주 날씨 & 조석 정보")

api = WeatherTideAPI()

# 제주 지역 선택 (기상청 격자좌표계와 조위관측소 코드 사용)
locations = {
    "제주": {"nx": 53, "ny": 38, "tide_code": "DT_0004", "lat": 33.527, "lon": 126.543},
    "서귀포": {"nx": 52, "ny": 33, "tide_code": "DT_0010", "lat": 33.24, "lon": 126.561},
    "성산포": {"nx": 55, "ny": 37, "tide_code": "DT_0022", "lat": 33.474, "lon": 126.927}
}

selected_location = st.selectbox(
    "지역을 선택하세요",
    list(locations.keys())
)

loc_info = locations[selected_location]

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 현재 날씨")
    weather_data = api.get_weather(loc_info["nx"], loc_info["ny"])
    
    if weather_data:
        st.metric("기온", f"{weather_data.get('temperature', 'N/A')}°C")
        st.metric("습도", f"{weather_data.get('humidity', 'N/A')}%")
        st.metric("강수량", f"{weather_data.get('rainfall', 'N/A')}mm")
        st.metric("풍속", f"{weather_data.get('wind_speed', 'N/A')}m/s")
    else:
        st.error("날씨 정보를 불러올 수 없습니다.")

with col2:
    st.subheader("🌊 조석 정보")
    with st.spinner("조석 정보를 불러오는 중..."):
        tide_data = api.get_tide(loc_info["tide_code"])
        
        if tide_data is not None and not tide_data.empty:
            tide_data = tide_data.sort_values('time')
            st.line_chart(tide_data.set_index('time')['tide_level'])
            
            high_tide = tide_data.loc[tide_data['tide_level'].idxmax()]
            low_tide = tide_data.loc[tide_data['tide_level'].idxmin()]
            
            st.write(f"🔺 만조: {high_tide['time']} ({high_tide['tide_level']:.1f}m)")
            st.write(f"🔻 간조: {low_tide['time']} ({low_tide['tide_level']:.1f}m)")
            
            # 현재 위치 정보 표시
            st.write(f"📍 관측소 위치: 위도 {loc_info['lat']}, 경도 {loc_info['lon']}")
        else:
            st.error("조석 정보를 불러올 수 없습니다.")

# 새로고침 버튼
if st.button("새로고침"):
    st.rerun()