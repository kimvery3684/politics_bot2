import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import random
from io import BytesIO

# --- [1. 기본 설정] ---
st.set_page_config(page_title="JJ 쇼츠 마스터 2호점 (최신판)", page_icon="🟡", layout="wide")

FONT_FILE = "NanumGothic-ExtraBold.ttf"
SAVE_DIR = "saved_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- [2. 멘트 데이터베이스 (기업/리더십 전용)] ---
VIRAL_QUESTIONS = [
    # 💰 재벌/기업
    "대한민국을 먹여 살리는\n진짜 '애국자'는 누구?",
    "내 상사로 모시고 싶은\n'워너비 CEO'는?",
    "지금 주식 전재산\n몰빵 한다면 어디?",
    "가장 혁신적인\n'미래의 리더'는?",
    "가장 검소하고\n인간미 넘치는 회장님은?",
    "한국판 아이언맨에\n가장 가까운 사람은?",
    "가장 옷 잘 입는\n'패션왕' 회장님은?",
    
    # 👑 리더십/능력 (1호점과 공유하지만 뉘앙스가 다름)
    "위기 상황에서 회사를\n구할 '해결사'는?",
    "추진력 하나는 탱크 같다!\n최고의 '불도저'는?",
    "해외 바이어를\n가장 잘 설득할 사람은?",
    "가장 과감하게\n투자할 것 같은 승부사는?",
    "10년 뒤, 세계 1위가\n되어있을 기업은?",
    "직원들에게 보너스\n가장 많이 줄 것 같은 사람은?",
    "가장 '스마트'해 보이는\n천재형 리더는?"
]

# --- [3. DB 데이터] ---
DB_BUSINESS = ["이재용", "정의선", "김승연", "최태원", "구광모", "신동빈"]
DB_OTHERS = ["백종원", "손흥민", "봉준호", "페이커"] 
ALL_NAMES = sorted(list(set(DB_BUSINESS + DB_OTHERS)))

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

def create_quiz_image(content_list, d):
    canvas = Image.new('RGB', (1080, 1920), d['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    font_top = get_font(d['top_fs'])
    font_bot = get_font(d['bot_fs'])
    font_label = get_font(d['label_fs'])

    # 상단 바
    draw.rectangle([(0, 0), (1080, d['top_h'])], fill=d['top_bg'])
    try:
        lines = d['top_text'].split('\n')
        total_text_h = (len(lines) * d['top_fs']) + ((len(lines) - 1) * d['top_lh'])
        current_y = (d['top_h'] - total_text_h) / 2 + d['top_y_adj']
        
        for i, line in enumerate(lines):
            fill_color = d['top_color_1'] if i == 0 else d['top_color_2']
            draw.text((540, current_y), line, font=font_top, fill=fill_color, anchor="mt")
            current_y += d['top_fs'] + d['top_lh']
    except: pass

    # 그리드
    grid_start_y = d['top_h']
    grid_end_y = 1920 - d['bot_h']
    grid_height = grid_end_y - grid_start_y
    cell_w, cell_h = 1080 // 2, grid_height // 2
    positions = [(0, grid_start_y), (cell_w, grid_start_y), (0, grid_start_y + cell_h), (cell_w, grid_start_y + cell_h)]

    for i, (pos, (name, img)) in enumerate(zip(positions, content_list)):
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
        
        label_h = d['label_h']
        label_y = pos[1] + cell_h - label_h
        draw.rectangle([pos[0], label_y, pos[0]+cell_w, pos[1]+cell_h], fill=d['label_bg'])
        draw.text((pos[0] + cell_w/2, label_y + label_h/2), name, font=font_label, fill=d['label_color'], anchor="mm")
        draw.rectangle([pos[0], pos[1], pos[0]+cell_w, pos[1]+cell_h], outline="black", width=2)

    # 하단 바
    draw.rectangle([(0, 1920 - d['bot_h']), (1080, 1920)], fill=d['bot_bg'])
    try:
        bot_text_x = 540
        bot_text_y = (1920 - (d['bot_h'] / 2)) + d['bot_y_adj']
        draw.text((bot_text_x, bot_text_y), d['bot_text'], font=font_bot, fill=d['bot_color'], anchor="mm", align="center", spacing=d['bot_lh'])
    except: pass
    
    return canvas

# --- [5. 메인 UI] ---
st.title("🟡 2호점: 옐로우 (기업/리더십 주제)")
col_L, col_R = st.columns([1, 1.3])

with col_L:
    st.header("1. 인물 구성")
    mode = st.radio("모드 선택", ["🎲 DB 랜덤", "✅ DB 선택", "🛠️ 완전 자유 입력"], index=2, horizontal=True)

    final_content = []

    if mode == "🛠️ 완전 자유 입력":
        st.info("원하는 이름과 사진을 4개 순서대로 넣으세요.")
        for i in range(4):
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1: input_name = st.text_input(f"{i+1}번 이름표", value=f"인물 {i+1}", key=f"custom_name_{i}")
                with c2: input_file = st.file_uploader(f"{i+1}번 사진", type=['jpg','png','jpeg'], key=f"custom_file_{i}")
                img_obj = None
                if input_file: img_obj = Image.open(input_file).convert("RGB")
                final_content.append((input_name, img_obj))

    elif mode == "✅ DB 선택":
        if 'c_names' not in st.session_state: st.session_state.c_names = ["김승연", "이재용", "정의선", "최태원"]
        sel = st.multiselect("4명 선택", ALL_NAMES, default=st.session_state.c_names[:4])
        current_selection = sel if len(sel) == 4 else (sel + ["김승연", "이재용", "정의선", "최태원"])[:4]
        st.write("---")
        with st.popover("📸 DB 사진 관리"):
            for name in current_selection:
                f = st.file_uploader(f"{name} 사진 업로드", type=['jpg','png','jpeg'], key=f"u_{name}")
                if f: save_uploaded_file(f, name)
        for name in current_selection:
            img = load_saved_image(name)
            final_content.append((name, img))

    else:
        if st.button("🔄 다시 뽑기", use_container_width=True): st.session_state.rand_names = random.sample(ALL_NAMES, 4)
        if 'rand_names' not in st.session_state: st.session_state.rand_names = ["김승연", "이재용", "정의선", "최태원"]
        current_selection = st.session_state.rand_names
        for name in current_selection:
            img = load_saved_image(name)
            final_content.append((name, img))

    st.header("💬 질문 설정")
    with st.container(border=True):
        if 'q_text' not in st.session_state: st.session_state.q_text = VIRAL_QUESTIONS[0]
        c_q1, c_q2 = st.columns([1, 2])
        with c_q1:
            if st.button("🎲 질문 랜덤", type="primary", use_container_width=True): st.session_state.q_text = random.choice(VIRAL_QUESTIONS)
        with c_q2:
            selected_q = st.selectbox("질문 목록", VIRAL_QUESTIONS, index=0)
            if selected_q != VIRAL_QUESTIONS[0]: st.session_state.q_text = selected_q

        top_text = st.text_area("상단 문구 (엔터로 1,2줄 구분)", st.session_state.q_text, height=80)
    
    st.header("🎨 디자인 (옐로우맛)")
    with st.expander("⬆️ 상단 바 (Top Bar) 설정", expanded=True):
        c_h1, c_h2 = st.columns(2)
        with c_h1: top_h = st.slider("배경 높이", 100, 600, 400)
        with c_h2: top_bg = st.color_picker("배경색", "#FFFF00", key="tbg") 
        
        st.markdown("---")
        col_t1, col_t2 = st.columns(2)
        with col_t1: top_fs = st.slider("🅰️ 글자 크기", 20, 150, 65)
        with col_t2: top_y_adj = st.slider("↕️ 글자 위치 조절", -200, 200, 0)
        
        st.caption("줄별 색상")
        c_tc1, c_tc2 = st.columns(2)
        with c_tc1: top_color_1 = st.color_picker("1번째 줄", "#000000", key="tc1") 
        with c_tc2: top_color_2 = st.color_picker("2번째 줄", "#000000", key="tc2")
        top_lh = st.slider("행간", 0, 150, 20)

    with st.expander("⬇️ 하단 바 설정", expanded=False):
        bot_text = st.text_area("하단 문구", "사진을 두번 톡톡 누르고,\n댓글 남겨주세요!!")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            bot_h = st.slider("배경 높이", 100, 600, 350, key="bh")
            bot_bg = st.color_picker("배경색", "#FFFF00", key="bbg")
        with col_b2:
            bot_fs = st.slider("글자 크기", 20, 150, 45, key="bfs")
            bot_color = st.color_picker("글자색", "#000000", key="bc")
        bot_lh = st.slider("행간", 0, 150, 20, key="blh")
        bot_y_adj = st.slider("위치 조절", -200, 200, 0, key="bya")

    with st.expander("🖼️ 사진 & 이름표 설정", expanded=False):
        img_zoom = st.slider("사진 확대", 1.0, 3.0, 1.0, 0.1)
        label_h = st.slider("이름표 높이", 30, 200, 80)
        label_fs = st.slider("이름 크기", 20, 100, 45)
        c3, c4 = st.columns(2)
        label_bg = c3.color_picker("이름표 배경", "#FF0000", key="lbg")
        label_color = c4.color_picker("이름표 글자", "#FFFF00", key="lc")
            
    bg_color = st.color_picker("전체 배경", "#FFFF00")

    design = {
        'bg_color': bg_color, 
        'top_text': top_text, 'top_h': top_h, 'top_fs': top_fs, 'top_lh': top_lh, 'top_y_adj': top_y_adj, 'top_bg': top_bg,
        'top_color_1': top_color_1, 'top_color_2': top_color_2, 
        'bot_text': bot_text, 'bot_h': bot_h, 'bot_fs': bot_fs, 'bot_lh': bot_lh, 'bot_y_adj': bot_y_adj, 'bot_bg': bot_bg, 'bot_color': bot_color,
        'label_h': label_h, 'label_fs': label_fs, 'label_bg': label_bg, 'label_color': label_color, 'img_zoom': img_zoom
    }

with col_R:
    st.subheader("🖼️ 결과물")
    if len(final_content) == 4:
        final_img = create_quiz_image(final_content, design)
        st.image(final_img, use_container_width=True)
        buf = BytesIO()
        final_img.save(buf, format="JPEG", quality=100)
        st.download_button("💾 이미지 다운로드", buf.getvalue(), "shorts_business.jpg", "image/jpeg", use_container_width=True)
    else:
        st.error("오류: 4명의 인물 데이터가 필요합니다.")