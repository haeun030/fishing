import streamlit as st 
import sqlite3

# 메인 페이지 내용만 포함
st.title("🎣 Fishing App에 오신 것을 환영합니다!")

st.markdown("""
### 우리의 낚시 앱을 소개합니다!

**주요 기능:**
- 실시간 날씨 정보 확인
- 최적의 낚시 포인트 추천
- 낚시 정보 공유 커뮤니티
- 낚시 기록 관리

### 시작하기
주소창에 '/fish'를 입력하거나 왼쪽 사이드바의 페이지 목록에서 선택하여 이동해보세요!
""")

# 추가적인 소개 내용
st.subheader("✨ 특별 기능")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🌊 실시간 조석 정보")
    st.write("정확한 조석 정보로 최적의 낚시 시간을 찾아보세요.")
    
with col2:
    st.markdown("#### 👥 커뮤니티")
    st.write("다른 낚시러들과 정보를 공유해보세요.")

# 데이터베이스 연결
conn = sqlite3.connect('fishing.db')
cursor = conn.cursor()