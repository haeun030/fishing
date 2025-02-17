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
            
            # 초단기실황 조회
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
                        elif category == 'VEC':   # 풍향
                            weather_data['wind_direction'] = float(item['obsrValue'])
                    
                    # 풍향을 16방위로 변환
                    if 'wind_direction' in weather_data:
                        directions = ['북', '북북동', '북동', '동북동', '동', '동남동', '남동', '남남동', 
                                    '남', '남남서', '남서', '서남서', '서', '서북서', '북서', '북북서']
                        idx = int((weather_data['wind_direction'] + 11.25) / 22.5)
                        weather_data['wind_direction_str'] = directions[idx % 16]
                    
                    return weather_data
            return None
        except Exception as e:
            st.error(f"날씨 정보 조회 중 오류 발생: {str(e)}")
            return None

    def get_wave_info(self, obs_code):
        try:
            url = "http://www.khoa.go.kr/api/oceangrid/obsWaveHight/search.do"
            
            params = {
                'ServiceKey': self.tide_api_key,
                'ObsCode': obs_code,
                'Date': datetime.now().strftime("%Y%m%d"),
                'ResultType': 'json'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'data' in data['result'] and data['result']['data']:
                    latest_data = data['result']['data'][-1]  # 최신 데이터
                    wave_info = {}
                    
                    # 각 필드에 대해 개별적으로 예외 처리
                    try:
                        wave_info['wave_height'] = float(latest_data.get('wave_height', 0))
                    except (ValueError, TypeError):
                        wave_info['wave_height'] = 0
                    
                    try:
                        wave_info['wave_period'] = float(latest_data.get('wave_period', 0))
                    except (ValueError, TypeError):
                        wave_info['wave_period'] = 0
                    
                    return wave_info
                else:
                    st.warning(f"{obs_code} 관측소의 파도 데이터가 없습니다.")
                    return {'wave_height': 0, 'wave_period': 0}
            else:
                st.warning("파도 정보 서버에 접속할 수 없습니다.")
                return {'wave_height': 0, 'wave_period': 0}
        except Exception as e:
            st.error(f"파도 정보 조회 중 오류 발생: {str(e)}")
            return {'wave_height': 0, 'wave_period': 0}

    def get_tide(self, obs_code):
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
                            'time': item['record_time'].split()[1],
                            'tide_level': float(item['tide_level']) / 10
                        })
                    return pd.DataFrame(tide_data)
            return None
        except Exception as e:
            st.error(f"조석 정보 조회 중 오류 발생: {str(e)}")
            return None

st.title("🌊 제주 날씨 & 조석 정보")

api = WeatherTideAPI()

# 제주 지역 선택
locations = {
    "제주시": {"nx": 53, "ny": 38, "tide_code": "DT_0004", "wave_code": "TW_0079", "lat": 33.527, "lon": 126.543},
    "서귀포": {"nx": 52, "ny": 33, "tide_code": "DT_0010", "wave_code": "TW_0080", "lat": 33.24, "lon": 126.561},
    "성산포": {"nx": 55, "ny": 37, "tide_code": "DT_0022", "wave_code": "TW_0091", "lat": 33.474, "lon": 126.927},
    "모슬포": {"nx": 52, "ny": 32, "tide_code": "DT_0008", "wave_code": "TW_0077", "lat": 33.214, "lon": 126.251},
    "애월": {"nx": 52, "ny": 38, "tide_code": "DT_0005", "wave_code": "TW_0078", "lat": 33.463, "lon": 126.309},
    "김녕": {"nx": 55, "ny": 39, "tide_code": "DT_0007", "wave_code": "TW_0082", "lat": 33.557, "lon": 126.753},
    "우도": {"nx": 55, "ny": 38, "tide_code": "DT_0023", "wave_code": "TW_0092", "lat": 33.506, "lon": 126.951}
}

selected_location = st.selectbox(
    "지역을 선택하세요",
    list(locations.keys())
)

loc_info = locations[selected_location]

# 3개의 컬럼으로 변경
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("☁️ 현재 날씨")
    weather_data = api.get_weather(loc_info["nx"], loc_info["ny"])
    
    if weather_data:
        st.metric("기온", f"{weather_data.get('temperature', 'N/A')}°C")
        st.metric("습도", f"{weather_data.get('humidity', 'N/A')}%")
        st.metric("강수량", f"{weather_data.get('rainfall', 'N/A')}mm")
        st.metric("풍속", f"{weather_data.get('wind_speed', 'N/A')}m/s")
        if 'wind_direction_str' in weather_data:
            st.metric("풍향", weather_data['wind_direction_str'])
    else:
        st.error("날씨 정보를 불러올 수 없습니다.")

with col2:
    st.subheader("🌊 파도 정보")
    wave_data = api.get_wave_info(loc_info["wave_code"])
    if wave_data:
        wave_height = wave_data['wave_height']
        wave_period = wave_data['wave_period']
        
        if wave_height > 0:
            st.metric("파고", f"{wave_height:.1f}m")
            
            # 파고 상태 설명 추가
            if wave_height < 0.5:
                st.info("잔잔한 바다 (파고 < 0.5m)")
            elif wave_height < 1.0:
                st.info("약간 잔잔한 바다 (파고 0.5-1.0m)")
            elif wave_height < 2.0:
                st.warning("약간 높은 파도 (파고 1.0-2.0m)")
            else:
                st.error("높은 파도 주의 (파고 > 2.0m)")
        else:
            st.info("파고 정보가 현재 제공되지 않습니다")
            
        if wave_period > 0:
            st.metric("파주기", f"{wave_period:.1f}초")
            
            # 파주기 설명 추가
            if wave_period > 0:
                st.info(f"파도가 {wave_period:.1f}초 간격으로 도달")
        else:
            st.info("파주기 정보가 현재 제공되지 않습니다")
    else:
        st.error("파도 정보를 불러올 수 없습니다.")

with col3:
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