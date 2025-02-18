import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from collections import defaultdict
import numpy as np

def load_data():
    df = pd.read_csv('Jeju_Fishing_Data.csv')
    df['Month'] = pd.to_datetime(df['Caught Time']).dt.month
    return df

def process_fishing_spots(df, selected_months, min_count):
    # 선택된 월의 데이터만 필터링
    df = df[df['Month'].isin(selected_months)]
    
    # 위치 반올림
    df['Latitude_Round'] = df['Latitude'].round(2)
    df['Longitude_Round'] = df['Longitude'].round(2)
    
    # 위치별, 월별, 어종별 카운트 계산
    location_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    for _, row in df.iterrows():
        location_key = (row['Latitude_Round'], row['Longitude_Round'])
        location_counts[location_key][row['Month']][row['Fish Species']] += 1
    
    # 핫스팟 생성
    hotspots = []
    for loc, month_data in location_counts.items():
        for month, species_counts in month_data.items():
            for species, count in species_counts.items():
                if count >= min_count:
                    hotspots.append({
                        'latitude': loc[0],
                        'longitude': loc[1],
                        'month': month,
                        'species': species,
                        'count': count
                    })
    
    return hotspots

def create_map(hotspots, selected_months):
    jeju_center = [33.389, 126.552]
    m = folium.Map(location=jeju_center, zoom_start=11)
    
    # 어종별 색상 매핑
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
              'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue']
    
    species_color = {}
    color_idx = 0
    
    # 선택된 월의 핫스팟만 필터링
    filtered_hotspots = [spot for spot in hotspots if spot['month'] in selected_months]
    
    # 마커 생성
    for spot in filtered_hotspots:
        if spot['species'] not in species_color:
            species_color[spot['species']] = colors[color_idx % len(colors)]
            color_idx += 1
        
        # 마커에 월 정보 추가
        folium.Marker(
            location=[spot['latitude'], spot['longitude']],
            popup=f"어종: {spot['species']}<br>수량: {spot['count']}마리<br>월: {spot['month']}월",
            tooltip=f"{spot['species']} ({spot['count']}마리)",
            icon=folium.Icon(color=species_color[spot['species']], icon='info-sign')
        ).add_to(m)
    
    # 범례 추가
    legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; 
                    border:2px solid grey; z-index:9999; 
                    background-color:white;
                    padding: 10px;
                    font-size:14px;">
        <p><strong>어종 색상 범례</strong></p>
    '''
    for species, color in species_color.items():
        legend_html += f'<p><i class="fa fa-map-marker fa-2x" style="color:{color}"></i> {species}</p>'
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def display_monthly_stats(df, hotspots, selected_months):
    st.subheader('월별 통계')
    
    # 탭 생성
    tab1, tab2 = st.tabs(["📊 월별 어획량", "📍 월별 핫스팟"])
    
    with tab1:
        # 월별 어획량 통계
        monthly_stats = df[df['Month'].isin(selected_months)].groupby(['Month', 'Fish Species']).size().unstack(fill_value=0)
        monthly_stats.index = monthly_stats.index.map(lambda x: f'{x}월')
        st.dataframe(monthly_stats, use_container_width=True)
    
    with tab2:
        # 월별 핫스팟 통계
        filtered_hotspots = [spot for spot in hotspots if spot['month'] in selected_months]
        if filtered_hotspots:
            hotspot_df = pd.DataFrame(filtered_hotspots)
            hotspot_df['month'] = hotspot_df['month'].map(lambda x: f'{x}월')
            hotspot_df.columns = ['위도', '경도', '월', '어종', '수량']
            st.dataframe(
                hotspot_df.sort_values(['월', '수량'], ascending=[True, False]),
                use_container_width=True
            )
        else:
            st.info('선택한 조건에 맞는 핫스팟이 없습니다.')

def main():
    st.title('제주 어류 분포 지도')
    
    # 데이터 로드
    df = load_data()
    
    # 사이드바 필터
    st.sidebar.header('필터 옵션')
    
    # 월 선택 필터
    months = sorted(df['Month'].unique())
    month_names = {i: f'{i}월' for i in range(1, 13)}
    selected_months = st.sidebar.multiselect(
        '월 선택',
        options=months,
        default=months[0],  # 기본값으로 첫 번째 월만 선택
        format_func=lambda x: month_names[x]
    )
    
    # 어종 선택 필터
    all_species = sorted(df['Fish Species'].unique())
    selected_species = st.sidebar.multiselect(
        '어종 선택',
        options=all_species,
        default=all_species[:5]
    )
    
    # 최소 수량 필터
    min_count = st.sidebar.slider('최소 수량 기준', 1, 20, 5)
    
    # 데이터 필터링
    filtered_df = df[df['Fish Species'].isin(selected_species)]
    
    if not selected_months:
        st.warning('표시할 월을 선택해주세요.')
        return
        
    # 핫스팟 처리
    hotspots = process_fishing_spots(filtered_df, selected_months, min_count)
    
    # 지도 생성 및 표시
    st.subheader('어류 분포 지도')
    m = create_map(hotspots, selected_months)
    folium_static(m)
    
    # 통계 표시
    display_monthly_stats(filtered_df, hotspots, selected_months)

if __name__ == "__main__":
    main()