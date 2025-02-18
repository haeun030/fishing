import streamlit as st
from database import Database
from datetime import datetime

# 세션 상태 확인
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("로그인이 필요한 서비스입니다.")
    st.stop()

st.title("⭐ 낚시배 리뷰")

db = Database()

# 탭 생성
tab1, tab2 = st.tabs(["리뷰 목록", "리뷰 작성"])

with tab1:
    st.subheader("📝 배별 리뷰")
    boats = db.get_boats()
    
    for boat in boats:
        with st.expander(f"🚤 {boat['name']} (선장: {boat['captain_name']})"):
            # 평균 평점 표시
            avg_rating = boat.get('avg_rating') or 0
            review_count = boat.get('review_count') or 0
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write("**평균 평점**")
                if review_count > 0:
                    st.write(f"{'⭐' * round(avg_rating)} ({avg_rating:.1f})")
                    st.write(f"*{review_count}개의 리뷰*")
                else:
                    st.write("아직 리뷰가 없습니다")
            
            with col2:
                st.write("**배 정보**")
                st.write(f"어종: {boat['fishInfo']}")
                st.write(f"정원: {boat['capacity']}명")
                if boat.get('description'):
                    st.write(f"설명: {boat['description']}")
            
            # 리뷰 목록
            st.markdown("---")
            reviews = db.get_boat_reviews(boat['id'])
            if reviews:
                for review in reviews:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {review['title']}")
                    with col2:
                        st.write(f"{'⭐' * review['rating']}")
                    
                    st.write(review['content'])
                    st.write(f"*{review['user_name']} - {datetime.strptime(review['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')}*")
                    st.markdown("---")
            else:
                st.info("아직 작성된 리뷰가 없습니다.")

with tab2:
    st.subheader("✍️ 새 리뷰 작성")
    
    # 사용자가 이용 완료한 배 목록 가져오기
    completed_boats = db.get_user_completed_reservations(st.session_state.username)
    
    if not completed_boats:
        st.info("아직 이용 완료한 낚시배가 없습니다. 낚시배 이용 후 리뷰를 작성할 수 있습니다.")
    else:
        with st.form("review_form"):
            # 배 선택
            boat_options = [(b['id'], f"{b['name']} ({b['reservation_date']})") 
                          for b in completed_boats]
            selected_boat = st.selectbox(
                "리뷰할 배 선택",
                options=boat_options,
                format_func=lambda x: x[1]
            )
            
            # 리뷰 입력
            title = st.text_input("제목")
            content = st.text_area(
                "내용",
                placeholder="낚시배 이용 경험을 자세히 공유해주세요!\n- 잡은 물고기 종류와 수량\n- 선장님의 친절도\n- 배의 청결도\n- 기타 도움될 만한 정보"
            )
            rating = st.slider("평점", 1, 5, 5)
            
            # 등록 버튼
            if st.form_submit_button("리뷰 등록"):
                if title and content:
                    success, message = db.add_review(
                        selected_boat[0],
                        st.session_state.username,
                        title,
                        content,
                        rating
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("제목과 내용을 모두 입력해주세요.")