import sqlite3
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_name='fishing.db'):
        self.db_name = db_name
        self.init_db()
    
    def hash_password(self, password):
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # 사용자 테이블 - BOOLEAN을 INTEGER로 변경
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    is_captain INTEGER DEFAULT 0, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 물고기 테이블
            c.execute('''
                CREATE TABLE IF NOT EXISTS fish (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    scientific_name TEXT,
                    description TEXT,
                    image_url TEXT
                )
            ''')

            # 배 테이블 추가
            c.execute('''
                CREATE TABLE IF NOT EXISTS boats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    fishInfo TEXT NOT NULL,
                    captain_username TEXT NOT NULL,
                    capacity INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (captain_username) REFERENCES users(username)
                )
            ''')

            # 예약 테이블 추가
            c.execute('''
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boat_id INTEGER NOT NULL,
                    user_username TEXT NOT NULL,
                    reservation_date DATE NOT NULL,
                    boats_fish TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (boat_id) REFERENCES boats(id),
                    FOREIGN KEY (user_username) REFERENCES users(username),
                    FOREIGN KEY (boats_fish) REFERENCES boats(fishInfo)
                    
                )
            ''')

                # 배의 물고기 기록 테이블 추가
            c.execute('''
                CREATE TABLE IF NOT EXISTS boat_fish_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boat_id INTEGER NOT NULL,
                    fish_id INTEGER NOT NULL,
                    catch_count INTEGER DEFAULT 1,
                    last_caught_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (boat_id) REFERENCES boats(id),
                    FOREIGN KEY (fish_id) REFERENCES fish(id)
                )
            ''')

                # 리뷰 테이블 추가
            c.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boat_id INTEGER NOT NULL,
                    user_username TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (boat_id) REFERENCES boats(id),
                    FOREIGN KEY (user_username) REFERENCES users(username)
                )
            ''')

             # 테스트 데이터 삽입
            if not c.execute('SELECT id FROM fish LIMIT 1').fetchone():
                # 물고기 데이터 추가
                test_fish = [
                    ('우럭', 'Sebastes schlegeli', '한국 연근해의 대표적인 고급 어종', 'image/uu123.jpg'),
                    ('광어', 'Paralichthys olivaceus', '회로 즐기는 대표적인 횟감', 'image/uu123.jpg'),
                    ('농어', 'Lateolabrax japonicus', '힘이 좋은 대형 어종', 'image/uu123.jpg'),
                    ('감성돔', 'Acanthopagrus schlegeli', '서해안의 대표적인 고급 어종', 'image/uu123.jpg'),
                    ('돌돔', 'Oplegnathus fasciatus', '남해안의 고급 어종', 'image/uu123.jpg')
                ]
                c.executemany('''
                    INSERT INTO fish (name, scientific_name, description, image_url)
                    VALUES (?, ?, ?, ?)
                ''', test_fish)

            # 선장 및 배 데이터
            if not c.execute('SELECT id FROM boats LIMIT 1').fetchone():
                # 선장 계정 생성
                captain_data = [
                    ('captain1', self.hash_password('test123'), '홍길동 선장', 1),
                    ('captain2', self.hash_password('test123'), '김선장', 1)
                ]
                c.executemany('''
                    INSERT OR IGNORE INTO users (username, password, name, is_captain)
                    VALUES (?, ?, ?, ?)
                ''', captain_data)

                # 배 데이터 추가
                boat_data = [
                    ('행복호', '제주 우럭 전문', '우럭, 감성돔, 돌돔을 주로 낚시합니다. 우럭 조황이 가장 좋습니다.', 'captain1', 8),
                    ('돌고래호', '서해 광어 전문', '광어, 우럭, 농어를 주로 낚시합니다. 광어 포인트를 가장 많이 알고 있습니다.', 'captain2', 12)
                ]
                c.executemany('''
                    INSERT INTO boats (name, description, fishInfo, captain_username, capacity)
                    VALUES (?, ?, ?, ?, ?)
                ''', boat_data)

                # 각 배의 물고기 기록 추가
                from datetime import datetime, timedelta
                base_date = datetime.now()

                # 행복호 기록
                c.execute("SELECT id FROM boats WHERE name='행복호'")
                happy_boat_id = c.fetchone()[0]
                happy_boat_records = [
                    (happy_boat_id, 1, 157, (base_date - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')),  # 우럭
                    (happy_boat_id, 4, 89, (base_date - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')),   # 감성돔
                    (happy_boat_id, 5, 45, (base_date - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'))    # 돌돔
                ]

                # 돌고래호 기록
                c.execute("SELECT id FROM boats WHERE name='돌고래호'")
                dolphin_boat_id = c.fetchone()[0]
                dolphin_boat_records = [
                    (dolphin_boat_id, 2, 203, (base_date - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')), # 광어
                    (dolphin_boat_id, 1, 78, (base_date - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')),  # 우럭
                    (dolphin_boat_id, 3, 42, (base_date - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'))   # 농어
                ]

                # 물고기 기록 삽입
                c.executemany('''
                    INSERT INTO boat_fish_records (boat_id, fish_id, catch_count, last_caught_at)
                    VALUES (?, ?, ?, ?)
                ''', happy_boat_records + dolphin_boat_records)

            conn.commit()

    def execute_query(self, query, params=()):
        """쿼리 실행 메서드"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            return c.execute(query, params)

    # Fish related methods
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
                SELECT f.*, cf.location, cf.caught_at
                FROM caught_fish cf
                JOIN fish f ON cf.fish_id = f.id
                WHERE cf.user_username = ?
                ORDER BY cf.caught_at DESC
            ''', (username,))
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]

    def record_caught_fish(self, username, fish_id, size=None, weight=None, location=None):
        """잡은 물고기 기록"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO caught_fish (user_username, fish_id, location)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, fish_id, location))
                conn.commit()
            return True, "물고기가 등록되었습니다!"
        except sqlite3.Error as e:
            return False, f"등록 중 오류가 발생했습니다: {str(e)}"

    # Boat reservation methods
    def get_boat_reservations(self, boat_id):
        """특정 배의 예약 목록 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT r.*, u.name as user_name
                FROM reservations r
                JOIN users u ON r.user_username = u.username
                WHERE r.boat_id = ? AND r.status = 'confirmed'
                ORDER BY r.reservation_date
            ''', (boat_id,))
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]

    def get_user_reservations(self, username):
        """사용자의 예약 목록 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT r.*, b.name as boat_name, u.name as captain_name
                FROM reservations r
                JOIN boats b ON r.boat_id = b.id
                JOIN users u ON b.captain_username = u.username
                WHERE r.user_username = ?
                ORDER BY r.reservation_date DESC
            ''', (username,))
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]

    def get_user_completed_reservations(self, username):
        """사용자가 이용 완료한 배 목록 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT DISTINCT b.id, b.name, r.reservation_date
                FROM reservations r
                JOIN boats b ON r.boat_id = b.id
                WHERE r.user_username = ?
                AND r.status = 'confirmed'
                AND r.reservation_date <= date('now')
                ORDER BY r.reservation_date DESC
            ''', (username,))
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]

    def cancel_reservation(self, reservation_id):
        """예약 취소"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE reservations
                    SET status = 'cancelled'
                    WHERE id = ?
                ''', (reservation_id,))
                conn.commit()
            return True, "예약이 취소되었습니다."
        except sqlite3.Error as e:
            return False, f"예약 취소 중 오류가 발생했습니다: {str(e)}"


    def register_user(self, username, password, name, is_captain=False):
        """사용자 등록"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                # 기존 사용자 확인
                c.execute('SELECT username FROM users WHERE username = ?', (username,))
                if c.fetchone():
                    return False, "이미 존재하는 아이디입니다."
                
                # 비밀번호 해싱
                hashed_password = self.hash_password(password)
                
                # is_captain을 INTEGER로 변환
                is_captain_int = 1 if is_captain else 0
                
                # 사용자 등록
                c.execute('''
                    INSERT INTO users (username, password, name, is_captain)
                    VALUES (?, ?, ?, ?)
                ''', (username, hashed_password, name, is_captain_int))
                conn.commit()
            return True, "회원가입이 완료되었습니다!"
        except sqlite3.Error as e:
            return False, f"회원가입 중 오류가 발생했습니다: {str(e)}"

    def verify_login(self, username, password):
        """로그인 검증"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                # 해싱된 비밀번호로 비교
                hashed_password = self.hash_password(password)
                c.execute('''
                    SELECT username, name, is_captain
                    FROM users
                    WHERE username = ? AND password = ?
                ''', (username, hashed_password))
                user = c.fetchone()
                
                if user:
                    return True, {
                        'username': user[0],
                        'name': user[1],
                        'is_captain': user[2]
                    }
                return False, None
        except sqlite3.Error as e:
            return False, None
        
    def get_boats(self):
        """모든 배 정보와 현재 예약 상황 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT 
                    b.*,
                    u.name as captain_name,
                    COUNT(CASE WHEN r.status = 'confirmed' AND r.reservation_date >= date('now') THEN 1 END) as current_reservations
                FROM boats b
                JOIN users u ON b.captain_username = u.username
                LEFT JOIN reservations r ON b.id = r.boat_id
                GROUP BY b.id
                ORDER BY b.name
            ''')
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]

    def make_reservation(self, boat_id, user_username, reservation_date):
        """배 예약"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                
                # 해당 날짜의 예약 현황 확인
                c.execute('''
                    SELECT COUNT(*) as count, b.capacity
                    FROM reservations r
                    JOIN boats b ON r.boat_id = b.id
                    WHERE r.boat_id = ? 
                    AND r.reservation_date = ? 
                    AND r.status = 'confirmed'
                    GROUP BY b.id
                ''', (boat_id, reservation_date))
                
                result = c.fetchone()
                if result:
                    current_count, max_capacity = result
                    if current_count >= max_capacity:
                        return False, "해당 날짜는 이미 정원이 가득 찼습니다."
                
                # 동일한 날짜에 이미 예약했는지 확인
                c.execute('''
                    SELECT id FROM reservations
                    WHERE user_username = ? 
                    AND reservation_date = ? 
                    AND status = 'confirmed'
                ''', (user_username, reservation_date))
                
                if c.fetchone():
                    return False, "해당 날짜에 이미 다른 예약이 있습니다."
                
                # 예약 생성
                c.execute('''
                    INSERT INTO reservations (boat_id, user_username, reservation_date, status)
                    VALUES (?, ?, ?, 'confirmed')
                ''', (boat_id, user_username, reservation_date))
                conn.commit()
                
            return True, "예약이 완료되었습니다!"
        except sqlite3.Error as e:
            return False, f"예약 중 오류가 발생했습니다: {str(e)}"

    def get_boat(self, boat_id):
        """특정 배 정보 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT b.*, u.name as captain_name 
                FROM boats b
                JOIN users u ON b.captain_username = u.username
                WHERE b.id = ?
            ''', (boat_id,))
            columns = [description[0] for description in c.description]
            row = c.fetchone()
            if row:
                boat = dict(zip(columns, row))
                boat['fish_types'] = boat['fishInfo']
                boat['max_capacity'] = boat['capacity']
                return boat
            return None

    def add_boat(self, name, description, captain_username, capacity, fishInfo):
        """새 배 등록"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                # 동일한 이름의 배가 있는지 확인
                c.execute('SELECT id FROM boats WHERE name = ?', (name,))
                if c.fetchone():
                    return False, "이미 같은 이름의 배가 등록되어 있습니다."
                
                c.execute('''
                    INSERT INTO boats (name, description, captain_username, capacity, fishInfo)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, description, captain_username, capacity, fishInfo))
                conn.commit()
            return True, "배가 등록되었습니다!"
        except sqlite3.Error as e:
            return False, f"배 등록 중 오류가 발생했습니다: {str(e)}"

    def make_reservation(self, boat_id, user_username, reservation_date):
        """배 예약"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                # 해당 날짜에 이미 예약이 있는지 확인
                c.execute('''
                    SELECT COUNT(*) 
                    FROM reservations 
                    WHERE boat_id = ? AND reservation_date = ? AND status = 'confirmed'
                ''', (boat_id, reservation_date))
                if c.fetchone()[0] > 0:
                    return False, "해당 날짜에 이미 예약이 있습니다."
                
                c.execute('''
                    INSERT INTO reservations (boat_id, user_username, reservation_date, status)
                    VALUES (?, ?, ?, 'confirmed')
                ''', (boat_id, user_username, reservation_date))
                conn.commit()
            return True, "예약이 완료되었습니다!"
        except sqlite3.Error as e:
            return False, f"예약 중 오류가 발생했습니다: {str(e)}"

    def get_boat_fish_records(self, boat_id=None):
        """배의 물고기 잡은 기록 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            if boat_id:
                query = '''
                    SELECT b.name as boat_name, f.name as fish_name, 
                           f.image_url, bfr.catch_count, 
                           u.name as captain_name, b.description
                    FROM boat_fish_records bfr
                    JOIN boats b ON bfr.boat_id = b.id
                    JOIN fish f ON bfr.fish_id = f.id
                    JOIN users u ON b.captain_username = u.username
                    WHERE b.id = ?
                    ORDER BY bfr.catch_count DESC
                '''
                params = (boat_id,)
            else:
                query = '''
                    SELECT b.name as boat_name, f.name as fish_name, 
                           f.image_url, bfr.catch_count, 
                           u.name as captain_name, b.description
                    FROM boat_fish_records bfr
                    JOIN boats b ON bfr.boat_id = b.id
                    JOIN fish f ON bfr.fish_id = f.id
                    JOIN users u ON b.captain_username = u.username
                    ORDER BY b.name, bfr.catch_count DESC
                '''
                params = ()
            
            c.execute(query, params)
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
        
    def get_captain_boats(self, captain_username):
        """특정 선장의 배 목록 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # 선장의 배 정보와 각 배의 예약 현황을 함께 조회
            c.execute('''
                SELECT 
                    b.*,
                    COUNT(DISTINCT r.id) as total_reservations,
                    COUNT(DISTINCT CASE WHEN r.status = 'confirmed' AND r.reservation_date >= date('now') THEN r.id END) as upcoming_reservations
                FROM boats b
                LEFT JOIN reservations r ON b.id = r.boat_id
                WHERE b.captain_username = ?
                GROUP BY b.id
                ORDER BY b.created_at DESC
            ''', (captain_username,))
            
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
        
    def get_boat_reviews(self, boat_id):
        """특정 배의 리뷰 목록 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT r.*, u.name as user_name
                FROM reviews r
                JOIN users u ON r.user_username = u.username
                WHERE r.boat_id = ?
                ORDER BY r.created_at DESC
            ''', (boat_id,))
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]

    def add_review(self, boat_id, user_username, title, content, rating):
        """리뷰 등록"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                c = conn.cursor()
                
                # 해당 배를 이용한 적이 있는지 확인
                c.execute('''
                    SELECT COUNT(*) FROM reservations
                    WHERE boat_id = ? 
                    AND user_username = ?
                    AND status = 'confirmed'
                    AND reservation_date <= date('now')
                ''', (boat_id, user_username))
                
                if c.fetchone()[0] == 0:
                    return False, "이용 완료한 배에 대해서만 리뷰를 작성할 수 있습니다."
                
                # 이미 리뷰를 작성했는지 확인
                c.execute('''
                    SELECT COUNT(*) FROM reviews
                    WHERE boat_id = ? AND user_username = ?
                ''', (boat_id, user_username))
                
                if c.fetchone()[0] > 0:
                    return False, "이미 리뷰를 작성하셨습니다."
                
                # 리뷰 등록
                c.execute('''
                    INSERT INTO reviews (boat_id, user_username, title, content, rating)
                    VALUES (?, ?, ?, ?, ?)
                ''', (boat_id, user_username, title, content, rating))
                conn.commit()
                
            return True, "리뷰가 등록되었습니다!"
        except sqlite3.Error as e:
            return False, f"리뷰 등록 중 오류가 발생했습니다: {str(e)}"

    def get_boats(self):
        """모든 배 정보와 평균 평점 조회"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT 
                    b.*,
                    u.name as captain_name,
                    COUNT(CASE WHEN r.status = 'confirmed' AND r.reservation_date >= date('now') THEN 1 END) as current_reservations,
                    AVG(rv.rating) as avg_rating,
                    COUNT(rv.id) as review_count
                FROM boats b
                JOIN users u ON b.captain_username = u.username
                LEFT JOIN reservations r ON b.id = r.boat_id
                LEFT JOIN reviews rv ON b.id = rv.boat_id
                GROUP BY b.id
                ORDER BY b.name
            ''')
            columns = [description[0] for description in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]