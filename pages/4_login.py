import streamlit as st
from database import Database
from session_manager import init_session, set_page

st.title("로그인")

# 로그인 폼
with st.form("login_form"):
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    col1, col2 = st.columns([1, 4])
    
    with col1:
        submit = st.form_submit_button("로그인")
    
    if submit:
        if username and password:
            db = Database()
            success, user_data = db.verify_login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.name = user_data['name']
                st.session_state.is_captain = user_data['is_captain']
                set_page('main')
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")
        else:
            st.error("아이디와 비밀번호를 모두 입력해주세요.")

# 회원가입 링크
st.markdown("---")
st.write("계정이 없으신가요?")
if st.button("회원가입"):
    set_page('signup')