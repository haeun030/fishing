import streamlit as st
import os
from datetime import datetime
import base64
from fastapi import FastAPI, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 저장 경로 설정
SAVE_DIR = "image"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def save_base64_image(base64_string, filepath):
    """base64 문자열을 이미지로 변환하여 저장"""
    try:
        # base64 prefix 제거 (있는 경우)
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
            
        # base64 디코딩
        image_data = base64.b64decode(base64_string)
        
        # 이미지로 변환
        image = Image.open(io.BytesIO(image_data))
        
        # 이미지 저장
        image.save(filepath)
        return True
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return False

# POST 요청 처리
@app.post("/text")
async def receive_image(request: Request):
    try:
        data = await request.json()
        image_text = data.get("image")
        if image_text:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"
            filepath = os.path.join(SAVE_DIR, filename)
            
            if save_base64_image(image_text, filepath):
                return {"status": "success", "message": "Image saved", "filename": filename}
            else:
                return {"status": "error", "message": "Failed to save image"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Streamlit 인터페이스
def main():
    st.title("Image Receiver")
    
    if os.path.exists(SAVE_DIR):
        files = [f for f in os.listdir(SAVE_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
        files.sort(reverse=True)
        
        st.subheader("Received Images")
        for file in files[:5]:
            image_path = os.path.join(SAVE_DIR, file)
            image = Image.open(image_path)
            st.image(image, caption=f"File: {file}", use_column_width=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        uvicorn.run(app, host="0.0.0.0", port=8501)
    else:
        main()