import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import random
from io import BytesIO

# --- [1. 기본 설정 및 영구 저장소] ---
st.set_page_config(page_title="JJ 쇼츠 마스터 2호점 (바이럴 에디션)", page_icon="🔥", layout="wide")

FONT_FILE = "NanumGothic-ExtraBold.ttf"
SAVE_DIR = "saved_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- [2. 바이럴 질문 50선 (조회수 폭발 치트키)] ---
VIRAL_QUESTIONS = [
    # 🔥 1. 논쟁/대결 (댓글 전쟁 유도)
    "차기 대통령으로\n누가 가장 적합합니까?",
    "대한민국을 구할\n유일한 구원투수는?",
    "지금 당장 대통령이\n되었으면 하는 사람은?",
    "끝까지 믿고\n함께 갈 수 있는 사람은?",
    "가장 정치를 잘한다고\n생각하는 인물은?",
    "보수의 심장,\n진정한 적임자는 누구?",
    "진보의 미래,\n누가 이끌어야 할까?",
    "위기의 대한민국,\n경제 살릴 해결사는?",
    "가장 강력한 리더십을\n가진 인물은?",
    "다음 대선,\n누가 이길 것 같습니까?",
    "가장 억울하게\n공격받는 사람은?",
    "토론 붙으면\n압살할 것 같은 사람은?",
    "가장 뚝심 있고\n소신 있는 인물은?",
    
    # 😡 2. 비판/매운맛 (참여 유도 최강)
    "가장 실망스러운\n행보를 보인 사람은?",
    "정계 은퇴가\n시급한 사람은?",
    "절대 용서할 수 없는\n최악의 인물은?",
    "가장 믿었는데\n배신감을 준 사람은?",
    "말만 번지르르하고\n실속 없는 사람은?",
    "가장 뻔뻔하다고\n생각되는 인물은?",
    "나라를 망치고 있는\n주범은 누구입니까?",
    "가장 '쇼'를\n많이 하는 것 같은 사람은?",
    "내로남불의\n아이콘은 누구입니까?",
    "거품이 가장\n많이 낀 인물은?",
    
    # 😍 3. 감성/이상형 (팬심 자극)
    "솔직히 실물이\n가장 잘생긴 사람은?",
    "젊었을 때\n인기 많았을 것 같은 사람은?",
    "내 사위/며느리 삼고 싶은\n참한 인물은?",
    "가장 옷을\n잘 입는 패셔니스타는?",
    "인상과 관상이\n가장 좋은 사람은?",
    "목소리가 가장\n신뢰감 있는 사람은?",
    "가장 인간적이고\n따뜻해 보이는 사람은?",
    "웃는 모습이\n가장 호감인 사람은?",
    
    # 🍻 4. 밸런스 게임/상황극 (재미 유도)
    "무인도에 딱 한 명\n데려간다면 누구?",
    "오늘 밤 딱 한 명과\n술 한잔 한다면?",
    "내 전 재산을\n맡겨도 될 사람은?",
    "학창 시절에\n반장 도맡아 했을 것 같은 사람은?",
    "유튜브 하면\n가장 대박 날 것 같은 사람은?",
    "노래방 가면\n분위기 제일 잘 띄울 사람은?",
    "가장 싸움을\n잘할 것 같은 사람은?",
    "돈 빌려달라고 하면\n바로 빌려줄 것 같은 사람은?",
    "가장 효도할 것 같은\n효자/효녀는?",
    
    # 🗳️ 5. 기타/호기심
    "차기 당 대표로\n누구를 밀어주시겠습니까?",
    "가장 똑똑한\n천재형 인물은 누구?",
    "가장 흙수저에서\n자수성가한 인물은?",
    "가장 카리스마\n넘치는 인물은?",
    "가장 팬덤이\n강력하다고 생각하는 사람은?",
    "다음 총선에서\n살아남을 사람은?",
    "가장 연설을\n잘한다고 생각하는 사람은?",
    "가장 청렴결백할 것\n같은 사람은?",
    "역대급 라이벌,\n최후의 승자는?"
]

# --- [3. 인물 데이터베이스] ---
DB_PRESIDENTS = ["윤석열", "문재인", "박근혜", "이명박", "노무현", "김대중", "김영삼", "노태우", "전두환", "박정희", "이승만"]
DB_FIRST_LADIES = ["김건희", "김정숙", "김혜경", "이순자", "권양숙", "손명순", "김옥숙"]
DB_POLITICIANS = ["한동훈", "이재명", "조국", "이준석", "오세훈", "홍준표", "나경원", "안철수", "원희룡", "정청래", "추미애", "고민정", "이낙연", "김동연", "유시민", "김어준", "인요한", "배현진", "장제원"]
ALL_NAMES = sorted(list(set(DB_PRESIDENTS + DB_FIRST_LADIES + DB_POLITICIANS)))

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

    # 상단 바
    draw.rectangle([(0, 0), (1080, d['top_h'])], fill=d['top_bg'])
    try:
        # 줄바꿈 처리 포함하여 중앙 정렬
        draw.text((540, d['top_h'] / 2), d['top_text'], font=font_top, fill=d['top_color'], anchor="mm", align="center", spacing=d['top_lh'])
    except: pass

    # 중앙 그리드
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
        
        # 줌/크롭
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

    # 하단 바
    draw.rectangle([(0, 1920 - d['bot_h']), (1080, 1920)], fill=d['bot_bg'])
    try:
        draw.text((540, 1920 - (d['bot_h'] / 2)), d['bot_text'], font=font_bot, fill=d['bot_color'], anchor="mm", align="center", spacing=d['bot_lh'])
    except: pass
    return canvas

# --- [5. 메인 UI] ---
st.title("🔥 쇼츠 조회수 폭발 생성기 (2호점)")
col_L, col_R = st.columns([1, 1.3])

with col_L:
    # 1. 인물 구성
    with st.expander("👥 인물 구성", expanded=True):
        mode = st.radio("방식", ["🎲 랜덤", "✅ 직접 선택"], horizontal=True, label_visibility="collapsed")
        if 'c_names' not in st.session_state: st.session_state.c_names = ["윤석열", "이재명", "한동훈", "조국"]
        
        if mode == "🎲 랜덤":
            if st.button("🔄 인물 랜덤 뽑기", type="secondary", use_container_width=True):
                st.session_state.c_names = random.sample(ALL_NAMES, 4)
        else:
            sel = st.multiselect("4명 선택", ALL_NAMES, default=st.session_state.c_names[:4])
            if len(sel) == 4: st.session_state.c_names = sel
        
        # 사진 등록 (간소화)
        st.write("---")
        cols = st.columns(4)
        for i, name in enumerate(st.session_state.c_names):
            with cols[i]:
                img = load_saved_image(name)
                if img: st.image(img, caption=name, use_container_width=True)
                else: st.caption(f"{name}\n(없음)")
        
        with st.popover("📸 사진 업로드 하기"):
            for name in st.session_state.c_names:
                f = st.file_uploader(f"{name} 사진", type=['jpg','png','jpeg'], key=f"u_{name}")
                if f: save_uploaded_file(f, name)

    # 2. 질문(멘트) 설정 - 핵심 기능
    st.header("💬 질문 설정 (조회수 치트키)")
    with st.container(border=True):
        # 질문 랜덤 뽑기 기능
        if 'q_text' not in st.session_state: st.session_state.q_text = VIRAL_QUESTIONS[0]
        
        c_q1, c_q2 = st.columns([1, 1])
        with c_q1:
            if st.button("🎲 질문 랜덤 돌리기", type="primary", use_container_width=True):
                st.session_state.q_text = random.choice(VIRAL_QUESTIONS)
        with c_q2:
            # 직접 선택 기능
            selected_q = st.selectbox("목록에서 고르기", VIRAL_QUESTIONS, index=VIRAL_QUESTIONS.index(st.session_state.q_text) if st.session_state.q_text in VIRAL_QUESTIONS else 0)
            if selected_q != st.session_state.q_text:
                st.session_state.q_text = selected_q

        top_text = st.text_area("상단 문구 수정", st.session_state.q_text, height=100)
    
    # 3. 디자인 정밀 조절
    with st.expander("🎨 디자인 상세 설정"):
        t_tab, p_tab, b_tab = st.tabs(["상단", "사진/이름", "하단"])
        with t_tab:
            top_h = st.slider("높이", 50, 600, 400, key="th")
            top_fs = st.slider("글자 크기", 20, 150, 65, key="tfs")
            top_lh = st.slider("줄간격", 0, 100, 20, key="tlh")
            c1, c2 = st.columns(2)
            top_bg = c1.color_picker("배경", "#000000", key="tbg")
            top_color = c2.color_picker("글자", "#FFFF00", key="tc")
        with p_tab:
            img_zoom = st.slider("사진 확대", 1.0, 3.0, 1.0, 0.1)
            label_h = st.slider("이름표 높이", 30, 200, 80)
            label_fs = st.slider("이름 글자", 20, 100, 45)
            c3, c4 = st.columns(2)
            label_bg = c3.color_picker("배경", "#FF0000", key="lbg")
            label_color = c4.color_picker("글자", "#FFFF00", key="lc")
        with b_tab:
            bot_text = st.text_area("하단 문구", "정답을 댓글에 달면 정답을\n알려드립니다!!")
            bot_h = st.slider("높이", 50, 600, 350, key="bh")
            bot_fs = st.slider("글자 크기", 20, 150, 40, key="bfs")
            c5, c6 = st.columns(2)
            bot_bg = c5.color_picker("배경", "#000000", key="bbg")
            bot_color = c6.color_picker("글자", "#FFFFFF", key="bc")
            
    bg_color = st.color_picker("전체 배경", "#000000")

    design = {
        'bg_color': bg_color, 'top_text': top_text, 'top_h': top_h, 'top_fs': top_fs, 'top_lh': top_lh, 'top_bg': top_bg, 'top_color': top_color,
        'bot_text': bot_text, 'bot_h': bot_h, 'bot_fs': bot_fs, 'bot_lh': 20, 'bot_bg': bot_bg, 'bot_color': bot_color,
        'label_h': label_h, 'label_fs': label_fs, 'label_bg': label_bg, 'label_color': label_color, 'img_zoom': img_zoom
    }

with col_R:
    st.subheader("🖼️ 결과물 확인")
    final_img = create_quiz_image(st.session_state.c_names, design)
    st.image(final_img, use_container_width=True)
    buf = BytesIO()
    final_img.save(buf, format="JPEG", quality=100)
    st.download_button("💾 이미지 다운로드", buf.getvalue(), "shorts_viral.jpg", "image/jpeg", use_container_width=True)