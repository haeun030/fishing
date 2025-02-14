# signup.py
import streamlit as st
import database as dd

def show_signup_page():
    st.title("회원가입")
    
    with st.form("signup_form"):
        name = st.text_input("이름")
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        
        if st.form_submit_button("가입하기"):
            if all([name, username, password]):
                db = dd.Database()
                success, message = db.register_user(username, password, name)
                if success:
                    st.success(message)
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("모든 필드를 입력해주세요.")
    
    # 로그인 페이지로 돌아가기
    st.markdown("---")
    if st.button("로그인 페이지로 돌아가기"):
        st.session_state.page = 'login'
        st.rerun()