import streamlit as st

def check_session():
    """세션 상태 확인"""
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("로그인이 필요한 서비스입니다.")
        return False
    return True

def check_captain():
    """선장 권한 확인"""
    if not check_session():
        return False
    if not st.session_state.get('is_captain', False):
        st.error("선장 계정만 접근할 수 있는 페이지입니다.")
        return False
    return True

def init_session():
    """세션 초기화"""
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

def set_page(page):
    """페이지 변경"""
    st.session_state.page = page
    st.rerun()