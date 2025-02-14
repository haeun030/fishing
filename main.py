# main.py
import streamlit as st 
from pages import login as lp
from pages import signup as su
from pages import fish as fi
import sqlite3

def show_main_content():
    st.title("🎣 Fishing App에 오신 것을 환영합니다!")
    
    st.markdown("""
    ### 우리의 낚시 앱을 소개합니다!
    
    **주요 기능:**
    - 실시간 날씨 정보 확인
    - 최적의 낚시 포인트 추천
    - 낚시 정보 공유 커뮤니티
    - 낚시 기록 관리
    
    ### 시작하기
    오른쪽 상단의 로그인 버튼을 클릭하여 서비스를 이용해보세요!
    """)
    
    # 추가적인 소개 내용
    st.subheader("✨ 특별 기능")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🌊 실시간 조석 정보")
        st.write("정확한 조석 정보로 최적의 낚시 시간을 찾아보세요.")
        
    with col2:
        st.markdown("#### 📱 모바일 지원")
        st.write("언제 어디서나 편리하게 이용할 수 있습니다.")
        
    with col3:
        st.markdown("#### 👥 커뮤니티")
        st.write("다른 낚시러들과 정보를 공유해보세요.")

def main():
    # 세션 상태 초기화
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

        # 사이드바 네비게이션
    if not st.session_state.logged_in:
        if st.sidebar.button("로그인"): 
            st.session_state.page = 'login'
    else:
        st.sidebar.write(f"환영합니다, {st.session_state.name}님!")
        
        # Fish 버튼 추가
        if st.sidebar.button("Fish"):
            st.session_state.page = 'fish'
            st.rerun()
        
        if st.sidebar.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.page = 'main'
            st.rerun()

    # 페이지 라우팅
    if st.session_state.page == 'main':
        show_main_content()
    elif st.session_state.page == 'login':
        lp.show_login_page()
    elif st.session_state.page == 'signup':
        su.show_signup_page()
    elif st.session_state.page == 'fish':
        fi.show_fish_page()
    
    conn = sqlite3.connect('fishing.db')
    cursor = conn.cursor()

if __name__ == "__main__":
    main()