import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import random
from io import BytesIO

# --- [1. 기본 설정] ---
st.set_page_config(page_title="JJ 쇼츠 마스터 2호점 (옐로우)", page_icon="🟡", layout="wide")

FONT_FILE = "NanumGothic-ExtraBold.ttf"
SAVE_DIR = "saved_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- [2. 노딱 방지 & 댓글 폭발 부정 질문 30선] ---
VIRAL_QUESTIONS = [
    # 😡 섹션 1: 무능/책임론
    "국가 발전을 가로막는\n가장 큰 걸림돌은?",
    "세금이 가장 아깝다고\n생각되는 인물은?",
    "밥값 못하고 자리만\n차지하는 사람은?",
    "위기 대처 능력이\n가장 부족한 사람은?",
    "서민의 삶을 전혀\n모르는 것 같은 사람은?",
    "대한민국 정치를\n후퇴시키는 주범은?",
    "말만 번지르르하고\n성과는 없는 사람은?",
    
    # 🤥 섹션 2: 위선/거짓말
    "앞뒤가 가장 다른\n내로남불의 화신은?",
    "선거 때와 딴판으로\n말 바꾼 사람은?",
    "가장 뻔뻔하게\n거짓말하는 인물은?",
    "국민을 기만한다고\n생각되는 사람은?",
    "가장 신뢰가\n가지 않는 입은?",
    "자신의 이익만 챙기는\n이기적인 인물은?",
    "사과할 줄 모르는\n오만한 태도의 인물은?",
    
    # 🛑 섹션 3: 심판/은퇴
    "정계 은퇴가 시급한\n0순위는 누구?",
    "다음 선거에서\n절대 뽑으면 안 될 사람은?",
    "당장 사퇴해야\n마땅한 사람은?",
    "정치판에서 영원히\n추방해야 할 사람은?",
    "보기만 해도\n채널 돌리고 싶은 사람은?",
    "역대 최악의\n정치인 1위는?",
    "절대 용서할 수 없는\n과오를 저지른 사람은?",
    
    # ⚔️ 섹션 4: 배신/갈등
    "우리를 가장\n실망시킨 배신자는?",
    "내부 총질로\n팀을 망치는 사람은?",
    "가장 억지 주장을\n펼치는 사람은?",
    "갈등과 분열을\n조장하는 원흉은?",
    "권력에 취해\n초심을 잃은 사람은?",
    "주변 간신들에게\n휘둘리는 사람은?",
    "쇼맨십만 있고\n진정성은 없는 사람은?",
    "가장 비호감이라고\n생각하는 인물은?"
]

# --- [3. 인물 데이터베이스] ---
DB_PRESIDENTS = ["윤석열", "문재인", "박근혜", "이명박", "노무현", "김대중", "김영삼", "노태우", "전두환", "박정희", "이승만"]
DB_FIRST_LADIES = ["김건희", "김정숙", "김혜경", "이순자", "권양숙", "손명순", "김옥숙"]
DB_CONSERVATIVE = ["한동훈", "이준석", "오세훈", "홍준표", "나경원", "안철수", "원희룡", "배현진", "주호영", "권성동", "장제원", "김기현", "인요한", "추경호"]
DB_PROGRESSIVE = ["이재명", "조국", "김동연", "이낙연", "추미애", "정청래", "고민정", "박주민", "김남국", "임종석", "유시민", "김어준", "박용진"]
DB_BUSINESS = ["이재용", "정의선", "김승연", "최태원"]

ALL_NAMES = sorted(list(set(DB_PRESIDENTS + DB_FIRST_LADIES + DB_CONSERVATIVE + DB_PROGRESSIVE + DB_BUSINESS)))

# --- [4. 기능 함수들] ---
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

def create_quiz_image(target_names, d):
    canvas = Image.new('RGB', (1080, 1920), d['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    font_top = get_font(d['top_fs'])
    font_bot = get_font(d['bot_fs'])
    font_label = get_font(d['label_fs'])

    # --- 1. 상단 바 그리기 ---
    draw.rectangle([(0, 0), (1080, d['top_h'])], fill=d['top_bg'])
    
    try:
        # 텍스트를 줄바꿈(\n) 기준으로 쪼갭니다.
        lines = d['top_text'].split('\n')
        
        # 전체 텍스트 덩어리의 높이 계산 (중앙 정렬을 위해)
        # 높이 = (줄 수 * 폰트크기) + ((줄 수 - 1) * 줄간격)
        total_text_h = (len(lines) * d['top_fs']) + ((len(lines) - 1) * d['top_lh'])
        
        # 시작 Y 좌표 계산 (박스 중앙 - 텍스트 절반 + 미세조정)
        current_y = (d['top_h'] - total_text_h) / 2 + d['top_y_adj']
        
        for i, line in enumerate(lines):
            # i가 0이면(첫번째 줄) -> 색상1, 그 외(두번째 줄 등) -> 색상2
            fill_color = d['top_color_1'] if i == 0 else d['top_color_2']
            
            # 한 줄씩 그리기 (가운데 정렬)
            # anchor="mt" (Middle Top) 기준
            draw.text((540, current_y), line, font=font_top, fill=fill_color, anchor="mt")
            
            # 다음 줄 Y 좌표로 이동
            current_y += d['top_fs'] + d['top_lh']

    except Exception as e:
        print(f"Text Error: {e}")
        pass

    # --- 2. 중앙 그리드 (사진 4장) ---
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
        
        # 이름표
        label_h = d['label_h']
        label_y = pos[1] + cell_h - label_h
        draw.rectangle([pos[0], label_y, pos[0]+cell_w, pos[1]+cell_h], fill=d['label_bg'])
        draw.text((pos[0] + cell_w/2, label_y + label_h/2), name, font=font_label, fill=d['label_color'], anchor="mm")
        draw.rectangle([pos[0], pos[1], pos[0]+cell_w, pos[1]+cell_h], outline="black", width=2)

    # --- 3. 하단 바 ---
    draw.rectangle([(0, 1920 - d['bot_h']), (1080, 1920)], fill=d['bot_bg'])
    try:
        bot_text_x = 540
        bot_text_y = (1920 - (d['bot_h'] / 2)) + d['bot_y_adj']
        draw.text((bot_text_x, bot_text_y), d['bot_text'], font=font_bot, fill=d['bot_color'], anchor="mm", align="center", spacing=d['bot_lh'])
    except: pass
    return canvas

# --- [5. 메인 UI] ---
st.title("🟡 2호점: 옐로우 에디션 (2줄 색상 분리)")
col_L, col_R = st.columns([1, 1.3])

with col_L:
    # 1. 인물 구성
    with st.expander("👥 인물 구성", expanded=True):
        mode = st.radio("방식", ["🎲 랜덤", "✅ 직접 선택"], horizontal=True, label_visibility="collapsed")
        
        if 'c_names' not in st.session_state: 
            st.session_state.c_names = ["김승연", "이재용", "정의선", "최태원"]
        
        if mode == "🎲 랜덤":
            if st.button("🔄 인물 랜덤 뽑기", type="secondary", use_container_width=True):
                st.session_state.c_names = random.sample(ALL_NAMES, 4)
        else:
            sel = st.multiselect("4명 선택", ALL_NAMES, default=st.session_state.c_names[:4])
            if len(sel) == 4: st.session_state.c_names = sel
        
        st.write("---")
        with st.popover("📸 사진 업로드 및 관리"):
            for name in st.session_state.c_names:
                f = st.file_uploader(f"{name} 사진", type=['jpg','png','jpeg'], key=f"u_{name}")
                if f: save_uploaded_file(f, name)
            st.info("등록된 사진은 'saved_images' 폴더에 자동 저장됩니다.")

    # 2. 질문(멘트) 설정
    st.header("💬 질문 설정")
    with st.container(border=True):
        if 'q_text' not in st.session_state: st.session_state.q_text = VIRAL_QUESTIONS[0]
        
        c_q1, c_q2 = st.columns([1, 1])
        with c_q1:
            if st.button("🎲 질문 랜덤", type="primary", use_container_width=True):
                st.session_state.q_text = random.choice(VIRAL_QUESTIONS)
        with c_q2:
            selected_q = st.selectbox("목록 선택", VIRAL_QUESTIONS, index=VIRAL_QUESTIONS.index(st.session_state.q_text) if st.session_state.q_text in VIRAL_QUESTIONS else 0)
            if selected_q != st.session_state.q_text:
                st.session_state.q_text = selected_q

        top_text = st.text_area("상단 문구 수정 (줄바꿈으로 1, 2줄 구분)", st.session_state.q_text, height=80)
    
    # 3. 디자인 정밀 조절
    st.header("🎨 디자인 초정밀 설정")
    
    with st.expander("⬆️ 상단 바 (Top Bar) 설정", expanded=True):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            top_h = st.slider("배경 높이", 100, 600, 400)
            top_bg = st.color_picker("배경색", "#000000", key="tbg") # 배경 검정 추천
        with col_t2:
            top_fs = st.slider("글자 크기", 20, 150, 65)
        
        st.markdown("---")
        st.caption("🎨 줄별 글자 색상 선택")
        c_tc1, c_tc2 = st.columns(2)
        with c_tc1:
            # 1번째 줄 색상
            top_color_1 = st.color_picker("1번째 줄 색상", "#FF0000", key="tc1") # 빨강 추천
        with c_tc2:
            # 2번째 줄 색상
            top_color_2 = st.color_picker("2번째 줄 색상", "#FFFFFF", key="tc2") # 흰색 추천

        st.markdown("---")
        top_lh = st.slider("행간 (줄 간격)", 0, 150, 20)
        top_y_adj = st.slider("글자 위치 (위/아래)", -200, 200, 0)

    with st.expander("⬇️ 하단 바 (Bottom Bar) 설정", expanded=False):
        bot_text = st.text_area("하단 문구", "인물을 두번 톡톡 누르고,\n댓글 남겨주세요!!")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            bot_h = st.slider("배경 높이", 100, 600, 350, key="bh")
            bot_bg = st.color_picker("배경색", "#FFFF00", key="bbg")
        with col_b2:
            bot_fs = st.slider("글자 크기", 20, 150, 45, key="bfs")
            bot_color = st.color_picker("글자색", "#000000", key="bc")
        
        st.markdown("---")
        bot_lh = st.slider("행간 (줄 간격)", 0, 150, 20, key="blh")
        bot_y_adj = st.slider("글자 위치 (위/아래)", -200, 200, 0, key="bya")

    with st.expander("🖼️ 사진 & 이름표 설정", expanded=False):
        img_zoom = st.slider("사진 확대", 1.0, 3.0, 1.0, 0.1)
        label_h = st.slider("이름표 높이", 30, 200, 80)
        label_fs = st.slider("이름 글자 크기", 20, 100, 45)
        c3, c4 = st.columns(2)
        label_bg = c3.color_picker("이름표 배경", "#FF0000", key="lbg")
        label_color = c4.color_picker("이름표 글자", "#FFFF00", key="lc")
            
    bg_color = st.color_picker("전체 배경 (빈공간)", "#FFFF00")

    design = {
        'bg_color': bg_color, 
        'top_text': top_text, 'top_h': top_h, 'top_fs': top_fs, 'top_lh': top_lh, 'top_y_adj': top_y_adj, 'top_bg': top_bg,
        'top_color_1': top_color_1, # [NEW] 1줄 색상
        'top_color_2': top_color_2, # [NEW] 2줄 색상
        'bot_text': bot_text, 'bot_h': bot_h, 'bot_fs': bot_fs, 'bot_lh': bot_lh, 'bot_y_adj': bot_y_adj, 'bot_bg': bot_bg, 'bot_color': bot_color,
        'label_h': label_h, 'label_fs': label_fs, 'label_bg': label_bg, 'label_color': label_color, 'img_zoom': img_zoom
    }

with col_R:
    st.subheader("🖼️ 결과물 확인")
    final_img = create_quiz_image(st.session_state.c_names, design)
    st.image(final_img, use_container_width=True)
    buf = BytesIO()
    final_img.save(buf, format="JPEG", quality=100)
    st.download_button("💾 이미지 다운로드", buf.getvalue(), "shorts_yellow.jpg", "image/jpeg", use_container_width=True)