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
            # 기존 users 테이블
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 물고기 정보 테이블
            c.execute('''
                CREATE TABLE IF NOT EXISTS fish (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    scientific_name TEXT,
                    description TEXT,
                    avg_size TEXT,
                    avg_weight TEXT,
                    image_url TEXT,
                    rarity TEXT
                )
            ''')
            
            # 사용자별 잡은 물고기 기록 테이블
            c.execute('''
                CREATE TABLE IF NOT EXISTS caught_fish (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    fish_id INTEGER,
                    caught_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    size TEXT,
                    weight TEXT,
                    location TEXT,
                    FOREIGN KEY (username) REFERENCES users(username),
                    FOREIGN KEY (fish_id) REFERENCES fish(id)
                )
            ''')
            
            # 기본 물고기 데이터 삽입
            self.insert_default_fish(c)
            conn.commit()
    
    def insert_default_fish(self, cursor):
        """기본 물고기 데이터 삽입"""
        img_url = "https://www.google.com/url?sa=i&url=http%3A%2F%2Fwww.foodnmed.com%2Fnews%2FarticleView.html%3Fidxno%3D14852&psig=AOvVaw3jHoUcgL3FG_FKuCKTBFRI&ust=1739645173501000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCLiyuufpw4sDFQAAAAAdAAAAABAY"
        default_fish = [
            ('우럭', 'Sebastes schlegeli', '바닷가 근처 암초지대에서 서식하는 농어목 우럭과의 물고기', '30-50cm', '1-3kg', img_url, '일반'),
            ('광어', 'Paralichthys olivaceus', '평평한 몸통을 가진 가자미목의 물고기', '40-60cm', '2-4kg', 'https://example.com/flounder.jpg', '일반'),
            ('참돔', 'Pagrus major', '온대성 어류로 연안의 암초지대에 서식', '50-70cm', '3-5kg', 'https://example.com/seabream.jpg', '희귀'),
        ]
        
        cursor.execute('SELECT COUNT(*) FROM fish')
        if cursor.fetchone()[0] == 0:  # 데이터가 없을 때만 삽입
            cursor.executemany('''
                INSERT INTO fish (name, scientific_name, description, avg_size, avg_weight, image_url, rarity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', default_fish)
    
    def get_all_fish(self):
        """모든 물고기 정보 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM fish')
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def get_caught_fish(self, username):
        """사용자가 잡은 물고기 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT f.*, c.caught_at, c.size, c.weight, c.location
                FROM caught_fish c
                JOIN fish f ON c.fish_id = f.id
                WHERE c.username = ?
                ORDER BY c.caught_at DESC
            ''', (username,))
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def record_caught_fish(self, username, fish_id, size=None, weight=None, location=None):
        """물고기 잡은 기록 추가"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO caught_fish (username, fish_id, size, weight, location)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, fish_id, size, weight, location))
                conn.commit()
            return True, "물고기 기록이 추가되었습니다!"
        except sqlite3.Error as e:
            return False, f"기록 추가 중 오류가 발생했습니다: {str(e)}"
    
    # 기존 메서드들...
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, name):
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