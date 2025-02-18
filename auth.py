from database import Database

class Auth:
    def __init__(self):
        self.db = Database()
    
    def register(self, username, password, name, is_captain=False):
        """회원가입"""
        return self.db.register_user(username, password, name, is_captain)
    
    def login(self, username, password):
        """로그인"""
        return self.db.verify_login(username, password)
    
    def logout(self):
        """로그아웃 - 세션 초기화"""
        import streamlit as st
        for key in ['logged_in', 'username', 'name', 'is_captain', 'page']:
            if key in st.session_state:
                del st.session_state[key]
        return True, "로그아웃되었습니다."