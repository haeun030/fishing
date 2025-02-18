import streamlit as st
from database import Database
from session_manager import check_captain, init_session
from datetime import datetime

init_session()
if not check_captain():
    st.stop()

st.title("⛵ 배 관리")

db = Database()

# 탭 생성
tab1, tab2 = st.tabs(["내 배 목록", "새 배 등록"])

with tab1:
    st.subheader("📋 등록된 배 목록")
    boats = db.get_captain_boats(st.session_state.username)
    
    if not boats:
        st.info("아직 등록된 배가 없습니다.")
    else:
        for boat in boats:
            with st.expander(f"🚤 {boat['name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**어종 정보:** {boat['fishInfo']}")
                    st.write(f"**정원:** {boat['capacity']}명")
                    if boat.get('description'):
                        st.write(f"**설명:** {boat['description']}")
                    
                    # 예약 통계
                    total_reservations = boat.get('total_reservations', 0)
                    upcoming_reservations = boat.get('upcoming_reservations', 0)
                    st.write(f"**전체 예약:** {total_reservations}건")
                    st.write(f"**예정된 예약:** {upcoming_reservations}건")
                
                with col2:
                    # 예약 현황
                    st.write("**🗓️ 예약 현황**")
                    reservations = db.get_boat_reservations(boat['id'])
                    if reservations:
                        for res in reservations:
                            reservation_date = datetime.strptime(res['reservation_date'], '%Y-%m-%d').date()
                            if reservation_date >= datetime.now().date():
                                st.write(f"- {res['reservation_date']}: {res['user_name']}")
                    else:
                        st.write("예정된 예약이 없습니다.")

with tab2:
    st.subheader("🆕 새 배 등록")
    with st.form("new_boat_form"):
        name = st.text_input("배 이름")
        fishInfo = st.text_area(
            "어종 정보",
            placeholder="예) 우럭, 광어 주요 포인트 보유\n광어 90% 이상의 조과율"
        )
        capacity = st.number_input("최대 정원", min_value=1, value=4)
        description = st.text_area(
            "상세 설명 (선택사항)", 
            placeholder="예) 제주 서귀포 출항\n오전 5시 출발, 오후 2시 귀항\n음료수, 간식 제공"
        )
        
        if st.form_submit_button("등록하기"):
            if name and fishInfo and capacity:
                success, message = db.add_boat(
                    name=name,
                    description=description,
                    captain_username=st.session_state.username,
                    capacity=capacity,
                    fishInfo=fishInfo
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("필수 항목을 모두 입력해주세요.")