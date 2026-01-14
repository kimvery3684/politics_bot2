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

# --- [2. 인물 데이터베이스] ---
DB_PRESIDENTS = ["윤석열", "문재인", "박근혜", "이명박", "노무현", "김대중", "김영삼", "노태우", "전두환", "박정희", "이승만"]
DB_FIRST_LADIES = ["김건희", "김정숙", "김혜경", "이순자", "권양숙", "손명순", "김옥숙"]
DB_POLITICIANS = ["한동훈", "이재명", "조국", "이준석", "오세훈", "홍준표", "나경원", "안철수", "원희룡", "정청래", "추미애", "고민정"]
ALL_NAMES = sorted(list(set(DB_PRESIDENTS + DB_FIRST_LADIES + DB_POLITICIANS)))

# --- [3. 영구 저장 및 불러오기 함수] ---
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

# --- [4. 이미지 생성 엔진 (디자인 변수 반영)] ---
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

    # 중앙 영역 계산
    grid_start_y = d['top_h']
    grid_end_y = 1920 - d['bot_h']
    grid_height = grid_end_y - grid_start_y
    cell_w, cell_h = 1080 // 2, grid_height // 2
    positions = [(0, grid_start_y), (cell_w, grid_start_y), (0, grid_start_y + cell_h), (cell_w, grid_start_y + cell_h)]

    for i, (name, pos) in enumerate(zip(target_names, positions)):
        img = load_saved_image(name)
        if img is None:
            img = Image.new('RGB', (cell_w, cell_h), (50, 50, 50))
            ImageDraw.Draw(img).text((cell_w/2, cell_h/2), f"{name}\n사진 없음", font=get_font(40), fill="white", anchor="mm", align="center")
        
        # 확대(Zoom) 및 크롭
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
            
        img = img.resize((cell_w, cell_h), Image.LANCZOS)
        canvas.paste(img, pos)
        
        # 이름표 디자인 반영
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
st.title("🏛️ 인물 퀴즈 2호점 (정밀 디자인 설정)")
col_L, col_R = st.columns([1, 1.3])

with col_L:
    # 1. 인물 구성
    with st.expander("👥 인물 구성 및 사진 등록", expanded=True):
        mode = st.radio("선택 방식", ["🎲 랜덤", "✅ 직접 선택"], horizontal=True)
        if 'c_names' not in st.session_state: st.session_state.c_names = ["윤석열", "이재명", "한동훈", "조국"]
        if mode == "🎲 랜덤":
            if st.button("🔄 무작위 4명 뽑기"): st.session_state.c_names = random.sample(ALL_NAMES, 4)
        else:
            sel = st.multiselect("4명 선택", ALL_NAMES, default=st.session_state.c_names[:4])
            if len(sel) == 4: st.session_state.c_names = sel
        
        st.write("---")
        for name in st.session_state.c_names:
            c1, c2 = st.columns([3, 1])
            with c1:
                f = st.file_uploader(f"'{name}' 사진", type=['jpg','png','jpeg'], key=f"u_{name}")
                if f:
                    if save_uploaded_file(f, name): st.success("saved!")
            with c2:
                img = load_saved_image(name)
                if img: st.image(img, width=50)

    # 2. 디자인 정밀 조절 (이미지 요청 사항 반영)
    st.header("🎚️ 디자인 세부 조절")
    
    with st.expander("⬆️ 상단 바 설정", expanded=False):
        top_text = st.text_area("상단 문구", "차기 대통령으로\n누구를\n가장 선호하나요?")
        top_h = st.slider("상단 높이", 50, 600, 400)
        top_fs = st.slider("상단 글자 크기", 20, 150, 55)
        top_lh = st.slider("상단 줄간격", 0, 100, 20)
        c1, c2 = st.columns(2)
        top_bg = c1.color_picker("배경색", "#000000", key="tbg")
        top_color = c2.color_picker("글자색", "#FFFF00", key="tc")

    with st.expander("🖼️ 사진 & 이름표 설정", expanded=True):
        img_zoom = st.slider("사진 확대 (Zoom)", 1.0, 3.0, 1.0, 0.1)
        st.markdown("---")
        label_h = st.slider("이름표 높이", 30, 200, 70)
        label_fs = st.slider("이름 글자 크기", 20, 100, 40)
        c3, c4 = st.columns(2)
        label_bg = c3.color_picker("이름표 배경", "#FF0000", key="lbg")
        label_color = c4.color_picker("이름표 글자", "#FFFF00", key="lc")

    with st.expander("⬇️ 하단 바 설정", expanded=False):
        bot_text = st.text_area("하단 문구", "정답을 댓글에 달면 정답을\n알려드립니다!!")
        bot_h = st.slider("하단 높이", 50, 600, 350)
        bot_fs = st.slider("하단 글자 크기", 20, 150, 40)
        bot_lh = st.slider("하단 줄간격", 0, 100, 20)
        c5, c6 = st.columns(2)
        bot_bg = c5.color_picker("배경색", "#000000", key="bbg")
        bot_color = c6.color_picker("글자색", "#FFFFFF", key="bc")
        
    bg_color = st.color_picker("전체 배경", "#000000")

    design = {
        'bg_color': bg_color, 'top_text': top_text, 'top_h': top_h, 'top_fs': top_fs, 'top_lh': top_lh, 'top_bg': top_bg, 'top_color': top_color,
        'bot_text': bot_text, 'bot_h': bot_h, 'bot_fs': bot_fs, 'bot_lh': bot_lh, 'bot_bg': bot_bg, 'bot_color': bot_color,
        'label_h': label_h, 'label_fs': label_fs, 'label_bg': label_bg, 'label_color': label_color, 'img_zoom': img_zoom
    }

with col_R:
    st.subheader("🖼️ 결과물 확인")
    final_img = create_quiz_image(st.session_state.c_names, design)
    st.image(final_img, use_container_width=True)
    buf = BytesIO()
    final_img.save(buf, format="JPEG", quality=100)
    st.download_button("💾 이미지 다운로드", buf.getvalue(), "quiz_final.jpg", "image/jpeg", use_container_width=True)