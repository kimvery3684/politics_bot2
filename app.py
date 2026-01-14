import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import random
from io import BytesIO

# --- [1. 기본 설정 및 영구 저장소] ---
st.set_page_config(page_title="JJ 쇼츠 마스터 2호점", page_icon="🏛️", layout="wide")

FONT_FILE = "NanumGothic-ExtraBold.ttf"
SAVE_DIR = "saved_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- [2. 인물 데이터베이스 (30명+30명+대통령+영부인)] ---
# 사용자님이 원하시는 명단을 여기에 자유롭게 추가/수정하세요.
DB_PRESIDENTS = ["윤석열", "문재인", "박근혜", "이명박", "노무현", "김대중", "김영삼", "노태우", "전두환", "박정희", "이승만"]
DB_FIRST_LADIES = ["김건희", "김정숙", "김혜경", "이순자", "권양숙", "손명순", "김옥숙"]
DB_CONSERVATIVE = [
    "한동훈", "이준석", "오세훈", "홍준표", "나경원", "안철수", "원희룡", "배현진", "주호영", "권성동", 
    "장제원", "김기현", "인요한", "김태호", "박진", "추경호", "이철규", "윤재옥", "조해진", "김도읍"
] # 추가로 30명까지 채우실 수 있습니다.
DB_PROGRESSIVE = [
    "이재명", "조국", "김동연", "이낙연", "추미애", "정청래", "고민정", "박주민", "김용민", "박지원", 
    "임종석", "유시민", "김어준", "박용진", "이탄희", "우상호", "송영길", "박홍근", "최강욱", "김남국"
] # 추가로 30명까지 채우실 수 있습니다.

ALL_NAMES = sorted(list(set(DB_PRESIDENTS + DB_FIRST_LADIES + DB_CONSERVATIVE + DB_PROGRESSIVE)))

# --- [3. 기능 함수] ---
def get_font(size):
    if os.path.exists(FONT_FILE): return ImageFont.truetype(FONT_FILE, size)
    else: return ImageFont.load_default()

def save_uploaded_file(uploaded_file, name):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            image.save(os.path.join(SAVE_DIR, f"{name}.jpg"), quality=95)
            return True
        except: return False
    return False

def load_saved_image(name):
    path = os.path.join(SAVE_DIR, f"{name}.jpg")
    if os.path.exists(path): return Image.open(path).convert("RGB")
    return None

# --- [4. 이미지 생성 엔진 (숫자 제거 & 줌 기능)] ---
def create_quiz_image(target_names, d):
    canvas = Image.new('RGB', (1080, 1920), d['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    font_top = get_font(d['top_fs'])
    font_bot = get_font(d['bot_fs'])
    font_label = get_font(d['label_fs'])

    # 상단 바
    draw.rectangle([(0, 0), (1080, d['top_h'])], fill=d['top_bg'])
    try:
        draw.text((540, d['top_h'] / 2), d['top_text'], font=font_top, fill=d['top_color'], anchor="mm", align="center", spacing=d['top_lh'])
    except: pass

    # 중앙 그리드 계산
    grid_start_y = d['top_h']
    grid_end_y = 1920 - d['bot_h']
    grid_height = grid_end_y - grid_start_y
    cell_w, cell_h = 1080 // 2, grid_height // 2
    positions = [(0, grid_start_y), (cell_w, grid_start_y), (0, grid_start_y + cell_h), (cell_w, grid_start_y + cell_h)]

    for i, (name, pos) in enumerate(zip(target_names, positions)):
        img = load_saved_image(name)
        if img is None:
            img = Image.new('RGB', (cell_w, cell_h), (50, 50, 50))
            ImageDraw.Draw(img).text((cell_w/2, cell_h/2), "사진 없음", font=get_font(40), fill="white", anchor="mm")
        
        # 줌 및 크롭
        zoom = d['img_zoom']
        img_ratio, target_ratio = img.width / img.height, cell_w / cell_h
        if img_ratio > target_ratio:
            new_w = int(img.height * target_ratio)
            img = img.crop(((img.width - new_w) // 2, 0, (img.width + new_w) // 2, img.height))
        else:
            new_h = int(img.width / target_ratio)
            img = img.crop((0, (img.height - new_h) // 2, img.width, (img.height + new_h) // 2))

        if zoom > 1.0:
            w, h = img.size
            cw, ch = int(w / zoom), int(h / zoom)
            img = img.crop(((w-cw)//2, (h-ch)//2, (w+cw)//2, (h+ch)//2))
            
        img_final = img.resize((cell_w, cell_h), Image.LANCZOS)
        canvas.paste(img_final, pos)
        
        # 이름표 (숫자 제거)
        label_h = d['label_h']
        label_y = pos[1] + cell_h - label_h
        draw.rectangle([pos[0], label_y, pos[0]+cell_w, pos[1]+cell_h], fill=d['label_bg'])
        draw.text((pos[0] + cell_w/2, label_y + label_h/2), name, font=font_label, fill=d['label_color'], anchor="mm")
        draw.rectangle([pos[0], pos[1], pos[0]+cell_w, pos[1]+cell_h], outline="black", width=2)

    # 하단 바
    draw.rectangle([(0, 1920 - d['bot_h']), (1080, 1920)], fill=d['bot_bg'])
    try:
        draw.text((540, 1920 - (d['bot_h'] / 2)), d['bot_text'], font=font_bot, fill=d['bot_color'], anchor="mm", align="center", spacing=d['bot_lh'])
    except: pass
    return canvas

# --- [5. 메인 UI] ---
st.title("🏛️ 정치인 퀴즈 2호점 (DB 탑재)")
col_L, col_R = st.columns([1, 1.3])

with col_L:
    st.subheader("👥 인물 구성")
    selection_mode = st.radio("구성 방식", ["🎲 랜덤", "✅ 직접 선택"], horizontal=True)
    if 'current_names' not in st.session_state: st.session_state.current_names = ["윤석열", "이재명", "한동훈", "조국"]

    if selection_mode == "🎲 랜덤":
        if st.button("🔄 무작위 4명 섞기"): st.session_state.current_names = random.sample(ALL_NAMES, 4)
    else:
        selected = st.multiselect("4명 선택", ALL_NAMES, default=st.session_state.current_names[:4])
        if len(selected) == 4: st.session_state.current_names = selected

    with st.expander("📸 사진 등록/관리", expanded=True):
        for name in st.session_state.current_names:
            c1, c2 = st.columns([3, 1])
            with c1:
                f = st.file_uploader(f"'{name}' 사진", type=['jpg','png','jpeg'], key=f"u_{name}")
                if f: save_uploaded_file(f, name)
            with c2:
                img = load_saved_image(name)
                if img: st.image(img, width=50)

    st.header("🎚️ 디자인 설정")
    with st.expander("상하단 레이아웃"):
        top_text = st.text_area("상단 문구", "다음 중 차기 대선에서\n가장 기대되는 인물은?")
        top_h = st.slider("상단 바 높이", 100, 600, 400)
        top_fs = st.slider("상단 글자 크기", 30, 150, 65)
        bot_text = st.text_area("하단 문구", "정답을 댓글에 달면 정답을 알려드립니다!!")
        bot_h = st.slider("하단 바 높이", 100, 600, 350)
        bot_fs = st.slider("하단 글자 크기", 20, 100, 45)

    with st.expander("사진 줌 & 이름표"):
        img_zoom = st.slider("사진 확대(Zoom)", 1.0, 3.0, 1.0, 0.1)
        label_h = st.slider("이름표 높이", 30, 200, 80)
        label_fs = st.slider("이름 글자 크기", 20, 100, 45)
        label_bg = st.color_picker("이름표 배경색", "#FF0000")
        label_color = st.color_picker("이름표 글자색", "#FFFF00")

    design = {
        'bg_color': "#000000", 'top_text': top_text, 'top_h': top_h, 'top_fs': top_fs, 'top_lh': 20, 'top_bg': "#000000", 'top_color': "#FFFF00",
        'bot_text': bot_text, 'bot_h': bot_h, 'bot_fs': bot_fs, 'bot_lh': 20, 'bot_bg': "#000000", 'bot_color': "#FFFFFF",
        'label_h': label_h, 'label_fs': label_fs, 'label_bg': label_bg, 'label_color': label_color, 'img_zoom': img_zoom
    }

with col_R:
    st.subheader("🖼️ 결과물 확인")
    final_img = create_quiz_image(st.session_state.current_names, design)
    st.image(final_img, use_container_width=True)
    buf = BytesIO()
    final_img.save(buf, format="JPEG", quality=100)
    st.download_button("💾 이미지 다운로드", buf.getvalue(), "quiz_2.jpg", "image/jpeg", use_container_width=True)