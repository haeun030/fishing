import streamlit as st
import requests


def show_fish_page():
# 생선 데이터를 불러오는 함수 (예제 데이터)
    FISH_DATA = {
        "salmon": {"name": "Salmon", "image": "https://example.com/salmon.png", "size": "50cm", "weight": "3kg"},
        "tuna": {"name": "Tuna", "image": "https://example.com/tuna.png", "size": "100cm", "weight": "10kg"},
        "bass": {"name": "Bass", "image": "https://example.com/bass.png", "size": "40cm", "weight": "2.5kg"}
    }

    caught_fish = st.session_state.get("caught_fish", set())

    # 스트림릿 UI 구성
    st.title("생선 낚시 도감")
    st.write("잡은 생선을 확인하세요!")

    # 잡은 생선 표시
    for fish, data in FISH_DATA.items():
        if fish in caught_fish:
            st.image(data["image"], caption=data["name"], width=200)
            st.write(f"**이름**: {data['name']}")
            st.write(f"**크기**: {data['size']}")
            st.write(f"**무게**: {data['weight']}")
        else:
            st.image("https://example.com/unknown.png", caption="???", width=200)
            st.write("**이름**: ???")
            st.write("**크기**: ???")
            st.write("**무게**: ???")

    # 생선 잡기 기능
    target_fish = st.text_input("생선 이름 입력", "salmon")
    if st.button("낚시하기"):
        if target_fish.lower() in FISH_DATA:
            caught_fish.add(target_fish.lower())
            st.session_state["caught_fish"] = caught_fish
            st.success(f"{FISH_DATA[target_fish.lower()]['name']}를 잡았습니다!")
        else:
            st.error("해당 생선을 찾을 수 없습니다!")
