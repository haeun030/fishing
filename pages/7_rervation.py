import streamlit as st
from database import Database
from datetime import datetime, timedelta

# 세션 상태 확인
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("로그인이 필요한 서비스입니다.")
    st.stop()

st.title("🎣 낚시배 예약")

db = Database()
boats = db.get_boats()

# 예약 가능한 배 목록 표시
st.subheader("📋 예약 가능한 배 목록")

if not boats:
    st.info("현재 예약 가능한 배가 없습니다.")
else:
    for boat in boats:
        with st.expander(f"🚤 {boat['name']} (선장: {boat['captain_name']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**어종 정보:** {boat['fishInfo']}")
                st.write(f"**정원:** {boat['capacity']}명")
                current_reservations = boat['current_reservations'] or 0
                st.write(f"**현재 예약:** {current_reservations}명")
                if boat.get('description'):
                    st.write(f"**설명:** {boat['description']}")
            
            with col2:
                # 예약 가능한 날짜 선택 (오늘부터 30일)
                min_date = datetime.now().date()
                max_date = min_date + timedelta(days=30)
                selected_date = st.date_input(
                    "예약일 선택",
                    min_value=min_date,
                    max_value=max_date,
                    key=f"date_{boat['id']}"
                )
                
                # 예약하기 버튼
                if st.button("예약하기", key=f"reserve_{boat['id']}"):
                    if current_reservations >= boat['capacity']:
                        st.error("죄송합니다. 이미 정원이 가득 찼습니다.")
                    else:
                        success, message = db.make_reservation(
                            boat['id'],
                            st.session_state.username,
                            selected_date.strftime("%Y-%m-%d")
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

# 내 예약 목록
st.markdown("---")
st.subheader("📅 내 예약 목록")

my_reservations = db.get_user_reservations(st.session_state.username)
if not my_reservations:
    st.info("예약 내역이 없습니다.")
else:
    for res in my_reservations:
        status_emoji = "✅" if res['status'] == 'confirmed' else "❌"
        with st.expander(f"🎣 {res['boat_name']} ({res['reservation_date']}) {status_emoji}"):
            st.write(f"**선장:** {res['captain_name']}")
            st.write(f"**상태:** {'예약 확정' if res['status'] == 'confirmed' else '취소됨'}")
            st.write(f"**예약일:** {res['reservation_date']}")
            
            # 예약 취소 버튼 (예약 확정 상태이고 예약일이 미래인 경우만 표시)
            reservation_date = datetime.strptime(res['reservation_date'], '%Y-%m-%d').date()
            if res['status'] == 'confirmed' and reservation_date > datetime.now().date():
                if st.button("예약 취소", key=f"cancel_{res['id']}"):
                    success, message = db.cancel_reservation(res['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)