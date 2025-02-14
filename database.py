# database.py
import sqlite3
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_name='fishing.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def hash_password(self, password):
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, name):
        """새 사용자 등록"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                hashed_pw = self.hash_password(password)
                c.execute(
                    'INSERT INTO users (username, password, name) VALUES (?, ?, ?)',
                    (username, hashed_pw, name)
                )
                conn.commit()
            return True, "회원가입이 완료되었습니다!"
        except sqlite3.IntegrityError:
            return False, "이미 존재하는 아이디입니다."
    
    def verify_login(self, username, password):
        """로그인 검증"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute(
                'SELECT password, name FROM users WHERE username = ?',
                (username,)
            )
            result = c.fetchone()
            
            if result and result[0] == self.hash_password(password):
                return True, {'name': result[1]}
            return False, None