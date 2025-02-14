# auth.py - 인증 관련 로직
import hashlib
from database import Database
import sqlite3

class Auth:
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password):
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, name):
        """회원가입"""
        try:
            hashed_pw = self.hash_password(password)
            self.db.execute_query(
                'INSERT INTO users (username, password, name) VALUES (?, ?, ?)',
                (username, hashed_pw, name)
            )
            return True, "회원가입이 완료되었습니다!"
        except sqlite3.IntegrityError:
            return False, "이미 존재하는 아이디입니다."
    
    def login(self, username, password):
        """로그인"""
        result = self.db.execute_query(
            'SELECT password, name FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        
        if result and result[0] == self.hash_password(password):
            return True, result[1]
        return False, None

