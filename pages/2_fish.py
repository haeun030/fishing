import streamlit as st
from database import Database

st.title("🎣 배별 조황 기록")

db = Database()
boats = db.get_boats()

# 배 선택 옵션
selected_boat = st.selectbox(
    "배 선택",
    ["전체 보기"] + [boat['name'] for boat in boats]
)

# 선택된 배의 물고기 기록 표시
if selected_boat == "전체 보기":
    records = db.get_boat_fish_records()
    
    # 배별로 그룹화하여 표시
    current_boat = None
    for record in records:
        if current_boat != record['boat_name']:
            st.markdown("---")
            st.subheader(f"⛵ {record['boat_name']}")
            st.write(f"선장: {record['captain_name']}")
            st.write(record['description'])
            current_boat = record['boat_name']
        
        # 물고기 정보 표시
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(record['image_url'], width=100)
        with col2:
            st.write(f"🐟 {record['fish_name']}")
            st.write(f"📊 잡은 횟수: {record['catch_count']}회")

else:
    # 특정 배의 정보만 표시
    selected_boat_id = next(boat['id'] for boat in boats if boat['name'] == selected_boat)
    records = db.get_boat_fish_records(selected_boat_id)
    
    if records:
        st.subheader(f"⛵ {records[0]['boat_name']}")
        st.write(f"선장: {records[0]['captain_name']}")
        st.write(records[0]['description'])
        
        # 물고기 정보를 그리드로 표시
        cols = st.columns(3)
        for idx, record in enumerate(records):
            with cols[idx % 3]:
                st.image(record['image_url'], width=150)
                st.write(f"🐟 {record['fish_name']}")
                st.write(f"📊 잡은 횟수: {record['catch_count']}회")