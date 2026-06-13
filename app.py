import streamlit as st
import streamlit.components.v1 as components
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
import os
import database as db
import config

# Initialize DB on start
db.init_db()

# Load questions helper
def get_questions_for_mode(mode):
    path = config.ENGLISH_QUESTIONS_PATH if mode == "English" else config.HINDI_QUESTIONS_PATH
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Set page config
st.set_page_config(
    page_title="Jainism course Online Exam Portal",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for premium interface
def inject_custom_css(dark_mode=False):
    card_bg = "#1e222b" if dark_mode else "#ffffff"
    card_border = "rgba(255, 255, 255, 0.1)" if dark_mode else "rgba(0, 0, 0, 0.08)"
    text_color = "#f0f2f6" if dark_mode else "#1c1e21"
    hover_bg = "rgba(255, 255, 255, 0.05)" if dark_mode else "rgba(0, 0, 0, 0.04)"
    radio_border = "rgba(255, 255, 255, 0.15)" if dark_mode else "rgba(0, 0, 0, 0.1)"
    
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Global font */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            font-family: 'Outfit', sans-serif !important;
        }}
        
        /* Gradient Banner for Headers */
        .header-banner {{
            background: linear-gradient(135deg, #FF8008 0%, #FFC837 100%);
            color: white !important;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(255, 128, 8, 0.25);
        }}
        .header-banner h1 {{
            color: white !important;
            font-weight: 700 !important;
            margin: 0 !important;
            font-size: 2.5rem !important;
        }}
        .header-banner p {{
            font-size: 1.1rem;
            margin-top: 8px !important;
            opacity: 0.9;
        }}
        
        /* Card Containers */
        .content-card {{
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
            margin-bottom: 25px;
            color: {text_color};
        }}
        
        /* Styled Options for st.radio */
        div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] {{
            display: none !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] {{
            gap: 10px;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] label {{
            background-color: {hover_bg};
            padding: 15px 20px;
            border-radius: 10px;
            border: 1px solid {radio_border};
            cursor: pointer;
            transition: all 0.2s ease;
            width: 100% !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {{
            background-color: {hover_bg};
            border-color: #FF8008;
            transform: translateX(4px);
        }}
        
        /* Navigation Sidebar Title */
        .sidebar-title {{
            font-size: 1.2rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #FF8008;
        }}
        
        /* Hide default link decoration for grid */
        .cbt-link:hover {{
            opacity: 0.8;
            transform: scale(1.05);
        }}

        /* Mobile responsiveness media queries */
        @media (max-width: 768px) {{
            .content-card {{
                padding: 15px !important;
                margin-bottom: 15px !important;
            }}
            .header-banner {{
                padding: 20px 15px !important;
                margin-bottom: 20px !important;
            }}
            .header-banner h1 {{
                font-size: 1.8rem !important;
            }}
            div[data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
                margin-bottom: 8px !important;
            }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Detect if Streamlit is in dark or light mode based on theme settings
# By default, we use light-mode styles, but let's check config if custom overrides exist
inject_custom_css(dark_mode=False)

# Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "register"
if "participant_id" not in st.session_state:
    st.session_state.participant_id = None
if "name" not in st.session_state:
    st.session_state.name = ""
if "age" not in st.session_state:
    st.session_state.age = ""
if "place" not in st.session_state:
    st.session_state.place = ""
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "mode" not in st.session_state:
    st.session_state.mode = "English"
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "flagged" not in st.session_state:
    st.session_state.flagged = set()
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_q_start_time" not in st.session_state:
    st.session_state.current_q_start_time = None
if "show_confirm_modal" not in st.session_state:
    st.session_state.show_confirm_modal = False

# View Routing via URL Parameters
view_param = st.query_params.get("view")
if view_param == "admin":
    if st.session_state.page != "admin":
        st.session_state.page = "admin"
        st.session_state.admin_logged_in = False
        st.rerun()
elif view_param == "candidate":
    if st.session_state.page == "admin":
        st.session_state.page = "register"
        st.session_state.admin_logged_in = False
        st.rerun()

# Process Query Parameters immediately
# Check if time runs out
if st.query_params.get("timeout") == "1" and st.session_state.page == "quiz":
    st.query_params.clear()
    # Auto-submit exam
    p_id = st.session_state.participant_id
    if p_id:
        score = 0
        for q in st.session_state.questions:
            q_id = str(q["id"])
            correct = q["answer"]
            user_ans = st.session_state.answers.get(q_id, None)
            if user_ans == correct:
                score += 1
        db.submit_exam(p_id, score, "timeout")
        st.session_state.page = "result"
        st.toast("⏳ Time's up! Your exam has been auto-submitted.", icon="⏰")
        st.rerun()

# Check if question timer runs out
if st.query_params.get("next_q") == "1" and st.session_state.page == "quiz":
    st.query_params.clear()
    if st.session_state.current_q_index < 99:
        st.session_state.current_q_index += 1
        st.session_state.current_q_start_time = time.time()
        st.toast("⏳ Question timer expired! Auto-advancing.", icon="⚠️")
        st.rerun()
    else:
        # Last question timeout, submit!
        p_id = st.session_state.participant_id
        if p_id:
            score = 0
            for q in st.session_state.questions:
                q_id = str(q["id"])
                correct = q["answer"]
                user_ans = st.session_state.answers.get(q_id, None)
                if user_ans == correct:
                    score += 1
            db.submit_exam(p_id, score, "timeout")
            st.session_state.page = "result"
            st.toast("⏳ Time's up! Your exam has been auto-submitted.", icon="⏰")
            st.rerun()

# Check if grid button clicked
q_param = st.query_params.get("q")
if q_param and st.session_state.page == "quiz":
    try:
        q_num = int(q_param)
        if 1 <= q_num <= 100:
            st.session_state.current_q_index = q_num - 1
            st.session_state.current_q_start_time = time.time()
            st.query_params.clear()
            st.rerun()
    except ValueError:
        pass

# ==========================================
# PAGE: REGISTRATION & ONBOARDING
# ==========================================
if st.session_state.page == "register":
    # Load and display logo
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(logo_path):
        col_logo_l, col_logo_c, col_logo_r = st.columns([1, 2, 1])
        with col_logo_c:
            st.image(logo_path, use_container_width=True)
            
    st.markdown(
        """
        <div class="header-banner" style="margin-top: 15px;">
            <h1 style="font-size: 2.0rem !important; line-height: 1.3;">Shri Vishwataarak Ratnatrayi Vidhya Raajitam Jainism Course</h1>
            <p style="font-size: 1.1rem; font-weight: 600; margin-top: 12px !important; color: #ffffff; opacity: 0.95;">
                Writer : Param Pujya Sadhviji Shri Maniprabha Shriji M S
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(
            """
            <div class="content-card">
                <h3 style="margin-top: 0; color: #FF8008;">Candidate Registration / अभ्यर्थी पंजीकरण</h3>
                <p style="font-size: 0.95rem; opacity: 0.85; margin-bottom: 20px;">
                    Please enter your correct credentials. If you previously registered and your session crashed, 
                    re-entering the exact same Phone Number will resume your exam session.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Registration Form
        name = st.text_input("Full Name / पूरा नाम", value=st.session_state.name)
        age_str = st.text_input("Age / आयु", value=str(st.session_state.age) if st.session_state.age else "")
        place = st.text_input("Place / स्थान (City/State)", value=st.session_state.place)
        phone = st.text_input("Phone Number / मोबाइल नंबर (10 Digits)", value=st.session_state.phone)
        mode = st.radio("Language Mode / परीक्षा का माध्यम", ["English", "Hindi"], index=0 if st.session_state.mode == "English" else 1, horizontal=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Start Exam / परीक्षा शुरू करें", type="primary", use_container_width=True):
            # Form Validation
            phone_clean = phone.strip().replace(" ", "")
            if not name.strip():
                st.error("Name field cannot be empty.")
            elif not age_str.strip() or not age_str.isdigit() or int(age_str) <= 0:
                st.error("Please enter a valid age.")
            elif not place.strip():
                st.error("Place field cannot be empty.")
            elif not phone_clean.isdigit() or len(phone_clean) != 10:
                st.error("Please enter a valid 10-digit Phone Number.")
            else:
                age = int(age_str)
                # Check for active session recovery
                active_session = db.get_active_participant_by_phone(phone_clean)
                
                if active_session:
                    st.toast("Active session found! Resuming your exam...", icon="🔄")
                    st.session_state.participant_id = active_session["id"]
                    st.session_state.name = active_session["name"]
                    st.session_state.age = active_session["age"]
                    st.session_state.place = active_session["place"]
                    st.session_state.phone = active_session["phone"]
                    st.session_state.mode = active_session["mode"]
                    st.session_state.start_time = active_session["start_time"]
                    st.session_state.answers = json.loads(active_session["answers"])
                    st.session_state.questions = get_questions_for_mode(active_session["mode"])
                    st.session_state.page = "quiz"
                    st.session_state.current_q_index = 0
                    st.session_state.current_q_start_time = time.time()
                    time.sleep(1)
                    st.rerun()
                else:
                    # Create new participant session
                    p_id = db.create_participant(name.strip(), age, place.strip(), phone_clean, mode)
                    st.session_state.participant_id = p_id
                    st.session_state.name = name.strip()
                    st.session_state.age = age
                    st.session_state.place = place.strip()
                    st.session_state.phone = phone_clean
                    st.session_state.mode = mode
                    st.session_state.start_time = time.time()
                    st.session_state.answers = {}
                    st.session_state.questions = get_questions_for_mode(mode)
                    st.session_state.page = "quiz"
                    st.session_state.current_q_index = 0
                    st.session_state.current_q_start_time = time.time()
                    st.toast("Registration complete! Exam started.", icon="✅")
                    time.sleep(1)
                    st.rerun()
                    
    with col2:
        st.markdown(
            """
            <div class="content-card" style="height: 100%;">
                <h4 style="margin-top: 0; color: #FF8008;">📜 Exam Instructions</h4>
                <ul style="font-size: 0.9rem; line-height: 1.5; padding-left: 20px;">
                    <li><strong>Total Questions:</strong> 100 MCQs</li>
                    <li><strong>Duration:</strong> 100 Minutes</li>
                    <li><strong>Time Limit:</strong> 1 Minute per question</li>
                    <li><strong>Submission:</strong> Automatic submission will trigger when the timer hits zero.</li>
                    <li><strong>Navigation:</strong> Use the Question Palette on the sidebar to jump to any question.</li>
                    <li><strong>Review:</strong> You can flag questions to review them later (marked in Orange).</li>
                </ul>
                <hr style="border: 0; border-top: 1px solid rgba(0,0,0,0.1); margin: 20px 0;">
                <p style="font-size: 0.85rem; text-align: center; color: #FF8008; font-weight: 500;">
                    Developed for the Jainism Course Examination
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ==========================================
# PAGE: QUIZ PANEL
# ==========================================
elif st.session_state.page == "quiz":
    # Ensure quiz questions are loaded
    if not st.session_state.questions:
        st.session_state.questions = get_questions_for_mode(st.session_state.mode)
        
    questions = st.session_state.questions
    q_index = st.session_state.current_q_index
    q = questions[q_index]
    q_id = q["id"]
    
    # Header Banner info
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 15px 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 1.1rem; font-weight: 600;">👤 Candidate: {st.session_state.name} | Language: {st.session_state.mode}</div>
            <div style="font-size: 1.1rem; font-weight: 600;">📝 Question {q_index + 1} of 100</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Calculate Timer values
    elapsed_seconds = time.time() - st.session_state.start_time
    total_allowed_seconds = config.TIME_LIMIT_MINUTES * 60
    remaining_seconds = max(0, int(total_allowed_seconds - elapsed_seconds))
    
    if remaining_seconds <= 0:
        # Submit automatically from backend just in case
        score = 0
        for q_item in st.session_state.questions:
            qi_id = str(q_item["id"])
            correct = q_item["answer"]
            user_ans = st.session_state.answers.get(qi_id, None)
            if user_ans == correct:
                score += 1
        db.submit_exam(st.session_state.participant_id, score, "timeout")
        st.session_state.page = "result"
        st.rerun()

    # Calculate Question Timer values
    if st.session_state.current_q_start_time is None:
        st.session_state.current_q_start_time = time.time()
        
    elapsed_q_seconds = time.time() - st.session_state.current_q_start_time
    remaining_q_seconds = max(0, int(60 - elapsed_q_seconds))
    
    # Backend check for question timer expiry
    if remaining_q_seconds <= 0:
        if st.session_state.current_q_index < 99:
            st.session_state.current_q_index += 1
            st.session_state.current_q_start_time = time.time()
            st.rerun()
        else:
            p_id = st.session_state.participant_id
            if p_id:
                score = 0
                for q_item in st.session_state.questions:
                    qi_id = str(q_item["id"])
                    correct = q_item["answer"]
                    user_ans = st.session_state.answers.get(qi_id, None)
                    if user_ans == correct:
                        score += 1
                db.submit_exam(p_id, score, "timeout")
                st.session_state.page = "result"
                st.rerun()

    # Inject client-side countdown timer in HTML (Horizontal on desktop, stacked on mobile)
    double_timer_html = f"""
    <div class="timer-container">
        <!-- Global Exam Timer -->
        <div class="timer-card exam-card">
            <span style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.6px; display: block; opacity: 0.85;">Total Exam Time</span>
            <span id="exam-timer" style="font-size: 20px;">100:00</span>
        </div>

        <!-- Question Timer -->
        <div class="timer-card q-card">
            <span style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.6px; display: block; opacity: 0.85;">Question Time Remaining</span>
            <span id="question-timer" style="font-size: 20px;">01:00</span>
        </div>
    </div>

    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: transparent;
            overflow: hidden;
        }}
        .timer-container {{
            display: flex;
            flex-direction: row;
            gap: 12px;
            width: 100%;
            box-sizing: border-box;
        }}
        .timer-card {{
            flex: 1;
            padding: 8px 12px;
            border-radius: 8px;
            color: white;
            text-align: center;
            font-family: 'Outfit', sans-serif;
            font-weight: bold;
        }}
        .exam-card {{
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            box-shadow: 0 4px 8px rgba(42, 82, 152, 0.2);
        }}
        .q-card {{
            background: linear-gradient(135deg, #FF4B4B, #FF8008);
            box-shadow: 0 4px 8px rgba(255, 75, 75, 0.2);
        }}
        
        @media (max-width: 600px) {{
            .timer-container {{
                flex-direction: column;
                gap: 8px;
            }}
        }}
    </style>

    <script>
        var examTime = {remaining_seconds};
        var questionTime = {remaining_q_seconds};
        
        function updateTimers() {{
            var examMin = Math.floor(examTime / 60);
            var examSec = examTime % 60;
            examMin = examMin < 10 ? '0' + examMin : examMin;
            examSec = examSec < 10 ? '0' + examSec : examSec;
            document.getElementById('exam-timer').innerText = examMin + ':' + examSec;
            
            var qMin = Math.floor(questionTime / 60);
            var qSec = questionTime % 60;
            qMin = qMin < 10 ? '0' + qMin : qMin;
            qSec = qSec < 10 ? '0' + qSec : qSec;
            document.getElementById('question-timer').innerText = qMin + ':' + qSec;
            
            if (examTime <= 0) {{
                clearInterval(timerInterval);
                window.parent.location.search = "?timeout=1";
            }} else if (questionTime <= 0) {{
                clearInterval(timerInterval);
                window.parent.location.search = "?next_q=1";
            }} else {{
                examTime--;
                questionTime--;
            }}
        }}
        
        updateTimers();
        var timerInterval = setInterval(updateTimers, 1000);
    </script>
    """
    components.html(double_timer_html, height=135)

    # ====================
    # SIDEBAR: PALETTE
    # ====================
    st.sidebar.markdown('<div class="sidebar-title">🧭 Palette</div>', unsafe_allow_html=True)
    
    # 5-column link-based CBT grid
    grid_html = "<div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; padding: 5px; max-height: 320px; overflow-y: auto;'>"
    for idx in range(100):
        q_num = idx + 1
        is_ans = str(q_num) in st.session_state.answers
        is_flg = q_num in st.session_state.flagged
        is_curr = idx == st.session_state.current_q_index
        
        # Determine button style
        if is_curr:
            border = "2px solid #FF8008"
            shadow = "0 0 6px rgba(255,128,8,0.6)"
        else:
            border = "1px solid rgba(255,255,255,0.15)"
            shadow = "none"
            
        if is_flg:
            bg = "#FF8008"  # Orange
            fg = "white"
        elif is_ans:
            bg = "#28A745"  # Green
            fg = "white"
        else:
            bg = "rgba(255,255,255,0.1)"  # Glassmorphic gray
            fg = "inherit"
            
        grid_html += f'<a href="?q={q_num}" target="_self" class="cbt-link" style="display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:6px;background-color:{bg};color:{fg} !important;font-size:11px;font-weight:bold;text-decoration:none;border:{border};box-shadow:{shadow};transition:all 0.15s ease;">{q_num}</a>'
    grid_html += "</div>"
    st.sidebar.markdown(grid_html, unsafe_allow_html=True)
    
    st.sidebar.markdown('<hr style="margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.15);">', unsafe_allow_html=True)
    
    # Palette Legend
    st.sidebar.markdown(
        """
        <div style="font-size: 0.8rem; line-height: 1.6; padding-left: 5px;">
            <div style="display: flex; align-items: center; margin-bottom: 5px;"><span style="display:inline-block; width:12px; height:12px; background:#28A745; border-radius:3px; margin-right:8px;"></span> Answered / उत्तर दिया गया</div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;"><span style="display:inline-block; width:12px; height:12px; background:#FF8008; border-radius:3px; margin-right:8px;"></span> Flagged for Review / समीक्षा के लिए चिह्नित</div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;"><span style="display:inline-block; width:12px; height:12px; background:rgba(255,255,255,0.15); border-radius:3px; margin-right:8px;"></span> Unanswered / अनुत्तरित</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("🔴 Submit Exam", type="primary", use_container_width=True):
        st.session_state.show_confirm_modal = True
        st.rerun()

    # ====================
    # MAIN AREA: QUESTION CARD
    # ====================
    st.markdown(
        f"""
        <div class="content-card">
            <div style="font-size: 0.95rem; text-transform: uppercase; color: #FF8008; font-weight: 600; margin-bottom: 8px;">Question {q_id}</div>
            <div style="font-size: 1.25rem; font-weight: 500; line-height: 1.5;">{q["question"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Option Selection
    options = q["options"]
    options_list = []
    options_map = {}
    for letter, text in options.items():
        label = f"{letter}. {text}"
        options_list.append(label)
        options_map[label] = letter
        
    current_ans = st.session_state.answers.get(str(q_id), None)
    default_idx = None
    if current_ans:
        for i, opt in enumerate(options_list):
            if opt.startswith(current_ans + "."):
                default_idx = i
                break
                
    st.markdown("<p style='font-size: 1rem; font-weight: 600; margin-bottom: 12px; color: #FF8008;'>Select Option / विकल्प चुनें:</p>", unsafe_allow_html=True)
    
    selected_option = st.radio(
        "options_radio",
        options_list,
        index=default_idx,
        key=f"radio_q_{q_id}_{q_index}",
        label_visibility="collapsed"
    )
    
    # Save answers on changes
    if selected_option:
        ans_letter = options_map[selected_option]
        if st.session_state.answers.get(str(q_id)) != ans_letter:
            st.session_state.answers[str(q_id)] = ans_letter
            db.update_answers(st.session_state.participant_id, st.session_state.answers)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action buttons row
    col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 1])
    
    with col_a:
        if st.button("⬅️ Previous", disabled=(q_index == 0), use_container_width=True):
            st.session_state.current_q_index -= 1
            st.session_state.current_q_start_time = time.time()
            st.rerun()
            
    with col_b:
        if st.button("Next ➡️", disabled=(q_index == 99), use_container_width=True):
            st.session_state.current_q_index += 1
            st.session_state.current_q_start_time = time.time()
            st.rerun()
            
    with col_c:
        is_flg = q_id in st.session_state.flagged
        flag_label = "🚩 Unflag" if is_flg else "🚩 Flag for Review"
        if st.button(flag_label, use_container_width=True):
            if is_flg:
                st.session_state.flagged.remove(q_id)
            else:
                st.session_state.flagged.add(q_id)
            st.rerun()
            
    with col_d:
        if st.button("🧹 Clear Choice", use_container_width=True):
            if str(q_id) in st.session_state.answers:
                del st.session_state.answers[str(q_id)]
                db.update_answers(st.session_state.participant_id, st.session_state.answers)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📊 View Question Palette / प्रश्न पैलेट देखें", expanded=False):
        st.markdown(grid_html, unsafe_allow_html=True)
                
    # ====================
    # SUBMIT CONFIRMATION MODAL (OVERLAY)
    # ====================
    if st.session_state.show_confirm_modal:
        st.markdown("<hr style='border-top:2px solid #FF8008;'>", unsafe_allow_html=True)
        st.warning("⚠️ **Confirm Exam Submission / परीक्षा जमा करने की पुष्टि करें**")
        
        answered_cnt = len(st.session_state.answers)
        st.write(f"You have answered **{answered_cnt}** out of 100 questions.")
        st.write("Are you sure you want to finish and submit the quiz? You cannot modify answers after submitting.")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            if st.button("✅ Yes, Submit Exam", use_container_width=True, type="primary"):
                # Calculate final score
                score = 0
                for q_item in st.session_state.questions:
                    qi_id = str(q_item["id"])
                    correct = q_item["answer"]
                    user_ans = st.session_state.answers.get(qi_id, None)
                    if user_ans == correct:
                        score += 1
                db.submit_exam(st.session_state.participant_id, score, "submitted")
                st.session_state.page = "result"
                st.session_state.show_confirm_modal = False
                st.toast("Quiz submitted successfully!", icon="✅")
                time.sleep(0.5)
                st.rerun()
        with m_col2:
            if st.button("❌ Cancel / परीक्षा जारी रखें", use_container_width=True):
                st.session_state.show_confirm_modal = False
                st.rerun()

# ==========================================
# PAGE: RESULTS DASHBOARD
# ==========================================
elif st.session_state.page == "result":
    st.markdown(
        """
        <div class="header-banner">
            <h1>🏆 Exam Results / परीक्षा परिणाम</h1>
            <p>Jainism Course assessment summary</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Fetch data
    p_id = st.session_state.participant_id
    if not p_id:
        st.warning("No participant record found.")
        if st.button("Back to Registration"):
            st.session_state.page = "register"
            st.rerun()
        st.stop()
        
    p_data = db.get_participant(p_id)
    if not p_data:
        st.error("Error loading candidate results.")
        st.stop()
        
    score = p_data["score"]
    answers = json.loads(p_data["answers"])
    mode = p_data["mode"]
    questions = get_questions_for_mode(mode)
    
    # Calculate detailed metrics
    total_q = len(questions)
    correct_cnt = score
    answered_cnt = len(answers)
    unattempted_cnt = total_q - answered_cnt
    incorrect_cnt = answered_cnt - correct_cnt
    accuracy = (correct_cnt / answered_cnt * 100) if answered_cnt > 0 else 0
    percentage = (correct_cnt / total_q) * 100
    
    # Duration Calculation
    start_t = p_data["start_time"]
    end_t = p_data["end_time"] if p_data["end_time"] else time.time()
    duration_minutes = int((end_t - start_t) / 60)
    duration_seconds = int((end_t - start_t) % 60)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown(
            f"""
            <div class="content-card" style="text-align: center;">
                <h3 style="margin: 0; color: #FF8008;">Scorecard / स्कोरकार्ड</h3>
                <div style="font-size: 4.5rem; font-weight: 700; color: #FF8008; margin: 15px 0;">
                    {score} <span style="font-size: 2rem; color: inherit; opacity: 0.6;">/ {total_q}</span>
                </div>
                <h4 style="margin: 0; opacity: 0.85;">Percentage: {percentage:.1f}%</h4>
                <p style="font-size: 0.9rem; opacity: 0.7; margin-top: 10px;">
                    Time Taken: {duration_minutes}m {duration_seconds}s
                </p>
                <hr style="border:0; border-top:1px solid rgba(0,0,0,0.1); margin: 20px 0;">
                <div style="display: flex; justify-content: space-around; text-align: center;">
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #28a745;">{correct_cnt}</div>
                        <div style="font-size: 0.8rem; opacity: 0.7;">Correct</div>
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #dc3545;">{incorrect_cnt}</div>
                        <div style="font-size: 0.8rem; opacity: 0.7;">Incorrect</div>
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #6c757d;">{unattempted_cnt}</div>
                        <div style="font-size: 0.8rem; opacity: 0.7;">Unattempted</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            """
            <div class="content-card" style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <h4 style="margin-top: 0; color: #FF8008; width: 100%; text-align: center;">Performance Chart</h4>
            """,
            unsafe_allow_html=True
        )
        # Donut chart of results
        plt.close('all')
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = ['Correct', 'Incorrect', 'Unattempted']
        sizes = [correct_cnt, incorrect_cnt, unattempted_cnt]
        colors = ['#28A745', '#DC3545', '#6C757D']
        
        # Remove labels if size is 0
        filtered_labels = [labels[i] for i in range(3) if sizes[i] > 0]
        filtered_sizes = [sizes[i] for i in range(3) if sizes[i] > 0]
        filtered_colors = [colors[i] for i in range(3) if sizes[i] > 0]
        
        wedges, texts, autotexts = ax.pie(
            filtered_sizes, 
            labels=filtered_labels, 
            colors=filtered_colors, 
            autopct='%1.0f%%', 
            startangle=90, 
            pctdistance=0.75,
            textprops=dict(color="w", weight="bold")
        )
        
        # Donut hole
        centre_circle = plt.Circle((0,0), 0.55, fc='white')
        fig.gca().add_artist(centre_circle)
        
        for t in texts:
            t.set_color('#1c1e21')
            t.set_fontsize(10)
            
        ax.axis('equal')  
        plt.tight_layout()
        fig.patch.set_alpha(0.0)
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="content-card" style="border-left: 5px solid #FF8008; padding: 25px;">
            <div style="font-weight: bold; color: #FF8008; font-size: 1.1rem; margin-bottom: 10px;">🔒 Examination Security / परीक्षा सुरक्षा</div>
            <div style="font-size: 0.95rem; line-height: 1.6;">
                To maintain the integrity of the examination, individual question reviews and correct answers are hidden. 
                This prevents answer leakage and ensures fairness for all participants. Your scorecard has been successfully 
                logged in the database and is visible to the administrator.
                <br><br>
                परीक्षा की अखंडता बनाए रखने के लिए, व्यक्तिगत प्रश्न समीक्षा और सही उत्तर छिपाए गए हैं। 
                यह उत्तरों के प्रकटीकरण को रोकता है और सभी प्रतिभागियों के लिए निष्पक्षता सुनिश्चित करता है। 
                आपका स्कोरकार्ड डेटाबेस में दर्ज हो गया है और प्रशासक को दिखाई दे रहा है।
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Log Out / Exit Portal", use_container_width=True):
        # Reset Session State
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==========================================
# PAGE: ADMIN DASHBOARD
# ==========================================
elif st.session_state.page == "admin":
    st.markdown(
        """
        <div class="header-banner" style="background: linear-gradient(135deg, #1f4068 0%, #162447 100%); box-shadow: 0 10px 25px rgba(31, 64, 104, 0.25);">
            <h1>🔑 Admin Console</h1>
            <p>Real-time Exam Monitoring & Results Portal</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Simple login mechanism
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
        
    if not st.session_state.admin_logged_in:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown(
                """
                <div class="content-card">
                    <h3 style="margin-top:0; color: #1f4068;">Admin Login</h3>
                    <p style="font-size: 0.9rem; opacity: 0.85;">Enter password to view live candidates' statistics and download spreadsheets.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            password = st.text_input("Enter Admin Password", type="password")
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                if st.button("🔑 Login", use_container_width=True, type="primary"):
                    if password == config.ADMIN_PASSWORD:
                        st.session_state.admin_logged_in = True
                        st.toast("Admin Logged In!", icon="🔓")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
            with sub_col2:
                if st.button("🏠 Exit Portal", use_container_width=True):
                    st.session_state.page = "register"
                    st.query_params["view"] = "candidate"
                    st.rerun()
        st.stop()
        
    # LOGGED IN VIEW
    # Navigation row
    n_col1, n_col2 = st.columns([1, 5])
    with n_col1:
        if st.button("🏠 Exit Admin Mode", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.page = "register"
            st.query_params["view"] = "candidate"
            st.rerun()
            
    # Load live statistics from SQLite DB
    results = db.get_all_results()
    
    if not results:
        st.info("No candidates have registered yet.")
        st.stop()
        
    df = pd.DataFrame(results)
    
    # Basic calculations
    total_registrations = len(df)
    submitted_df = df[df["score"] != -1]
    total_submitted = len(submitted_df)
    in_progress = total_registrations - total_submitted
    
    avg_score = submitted_df["score"].mean() if total_submitted > 0 else 0
    max_score = submitted_df["score"].max() if total_submitted > 0 else 0
    min_score = submitted_df["score"].min() if total_submitted > 0 else 0
    
    # Display Stats Cards
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        st.metric("Total Candidates Registered", total_registrations)
    with s_col2:
        st.metric("Exams Submitted", total_submitted, f"{in_progress} In Progress")
    with s_col3:
        st.metric("Average Score", f"{avg_score:.1f} / 100" if total_submitted > 0 else "N/A")
    with s_col4:
        st.metric("Top Score", f"{max_score} / 100" if total_submitted > 0 else "N/A")
        
    csv_df = df.copy()
    csv_df["start_time"] = csv_df["start_time"].apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x)) if pd.notna(x) else "N/A")
    csv_df["end_time"] = csv_df["end_time"].apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x)) if pd.notna(x) else "N/A")
    
    # Download Button
    csv = csv_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Real-time Results CSV",
        data=csv,
        file_name='jainism_exam_results.csv',
        mime='text/csv',
        use_container_width=True
    )
    
    # Display Data Table
    st.markdown("### 📋 Live Candidate Registrations")
    
    # Format table for display
    display_df = csv_df.drop(columns=["answers"])
    display_df.columns = ["ID", "Name", "Age", "Place", "Phone", "Language Mode", "Start Time", "End Time", "Score", "Status"]
    
    st.dataframe(display_df, use_container_width=True)
    
    # Advanced Reset Utility
    st.markdown("<br><hr style='border-top:1px solid rgba(0,0,0,0.1);'><br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Admin Utilities")
    
    confirm_wipe = st.checkbox("Confirm database reset warning: This deletes all candidate records and scores permanently.")
    if st.button("🗑️ Wipe Database / Wipe Results", disabled=not confirm_wipe, type="primary"):
        db.reset_db()
        st.toast("Database wiped successfully!", icon="💥")
        time.sleep(1)
        st.rerun()
