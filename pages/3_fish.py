# 3_fish.py
import streamlit as st
from database import Database
import pandas as pd
from datetime import datetime

# 세션 상태 확인
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("로그인이 필요한 서비스입니다.")
    st.stop()

# 데이터베이스 연결
db = Database()

st.title("🐟 나의 도감")

# 탭 생성
tab1, tab2 = st.tabs(["도감", "물고기 등록"])

with tab1:
    # 전체 물고기 목록 가져오기
    all_fish = db.get_all_fish()
    # 사용자가 잡은 물고기 목록 가져오기
    caught_fish = db.get_caught_fish(st.session_state.username)
    caught_fish_ids = {fish['id'] for fish in caught_fish}
    
    st.subheader("📚 물고기 도감")
    st.write(f"총 {len(all_fish)}종 중 {len(caught_fish_ids)}종 발견!")
    
    # 물고기 목록을 그리드로 표시
    cols = st.columns(3)
    for idx, fish in enumerate(all_fish):
        with cols[idx % 3]:
            if fish['id'] in caught_fish_ids:
                # 발견한 물고기
                st.image(fish['image_url'], caption=fish['name'], width=200)
                st.markdown(f"**{fish['name']}** ({fish['scientific_name']})")
                st.write(fish['description'])
                st.markdown(f"평균 크기: {fish['avg_size']}")
                st.markdown(f"평균 무게: {fish['avg_weight']}")
                st.markdown(f"희귀도: {fish['rarity']}")
                
                # 이 물고기의 잡은 기록 표시
                fish_records = [f for f in caught_fish if f['id'] == fish['id']]
                if fish_records:
                    with st.expander("잡은 기록 보기"):
                        for record in fish_records:
                            caught_date = datetime.strptime(record['caught_at'], 
                                '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                            st.write(f"📅 {caught_date}")
                            if record['location']:
                                st.write(f"📍 {record['location']}")
                            if record['size']:
                                st.write(f"📏 {record['size']}")
                            if record['weight']:
                                st.write(f"⚖️ {record['weight']}")
                            st.markdown("---")
            else:
                # 미발견 물고기
                st.image("image/uu123.jpg", caption="???", width=200)
                st.markdown("**???**")
                st.write("아직 발견하지 못한 물고기입니다.")

with tab2:
    st.subheader("🎣 물고기 등록")
    
    # 모든 물고기 정보 가져오기
    all_fish = db.get_all_fish()
    fish_names = [fish['name'] for fish in all_fish]
    fish_dict = {fish['name']: fish['id'] for fish in all_fish}
    
    with st.form("record_fish_form"):
        # 물고기 선택
        selected_fish = st.selectbox("잡은 물고기", fish_names)
        
        # 상세 정보 입력
        col1, col2 = st.columns(2)
        with col1:
            size = st.text_input("크기 (cm)", placeholder="예: 45cm")
            location = st.text_input("위치", placeholder="예: 부산 해운대")
        with col2:
            weight = st.text_input("무게 (kg)", placeholder="예: 2.5kg")
        
        if st.form_submit_button("등록하기"):
            if selected_fish:
                fish_id = fish_dict[selected_fish]
                success, message = db.record_caught_fish(
                    st.session_state.username,
                    fish_id,
                    size,
                    weight,
                    location
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("물고기를 선택해주세요.")