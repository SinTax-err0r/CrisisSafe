import streamlit as st
from rules import analyze_content
from datetime import datetime
import base64
import random
import os
import textwrap

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CrisisSafe",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- BACKGROUND IMAGES LOGIC ----------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

background_images = [
    "Newspaper1.png", "Newspaper2.png", "magazine1.png", "newspaper3.png", "poster1.png"
]

bg_css = ""
for i, img_name in enumerate(background_images):
    if os.path.exists(img_name):
        b64_data = get_base64_of_bin_file(img_name)
        # Random parameters for organic feel
        top = random.randint(0, 90)
        left = random.randint(0, 90)
        width = random.randint(200, 400)
        rotation = random.randint(-20, 20)
        duration = random.randint(20, 60) # Slow movement
        
        bg_css += f"""
        .floating-bg-{i} {{
            position: fixed;
            top: {top}vh;
            left: {left}vw;
            width: {width}px;
            opacity: 0.2;
            transform: rotate({rotation}deg);
            z-index: 0;
            pointer-events: none;
            animation: float-{i} {duration}s infinite alternate ease-in-out;
            background-image: url("data:image/png;base64,{b64_data}");
            background-size: contain;
            background-repeat: no-repeat;
            height: {width}px; /* Appr aspect ratio */
        }}
        
        @keyframes float-{i} {{
            0% {{ transform: rotate({rotation}deg) translate(0, 0); }}
            100% {{ transform: rotate({rotation + 5}deg) translate({random.randint(-20, 20)}px, {random.randint(-20, 20)}px); }}
        }}
        """

# ---------------- VICTORIAN IMPERIAL NEWSPAPER CSS ----------------
# Dynamic CSS for background
st.markdown(f"<style>{bg_css}</style>", unsafe_allow_html=True)

# Static CSS
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Libre+Baskerville:wght@400;700&family=Old+Standard+TT:wght@400;700&display=swap');

/* GLOBAL RESET */
body, .stApp {
    background-color: #e8e3d5 !important;
    color: #1a1410 !important;
    font-family: 'Libre Baskerville', 'Georgia', serif;
    opacity: 1 !important;
}

/* MAIN CONTENT AREA - aged paper texture */
.main .block-container {
    background-color: #e8e3d5;
    background-image:
        radial-gradient(circle at 20% 50%, rgba(139, 115, 85, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(139, 115, 85, 0.03) 0%, transparent 50%),
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 1px,
            rgba(90,70,50,0.02) 1px,
            rgba(90,70,50,0.02) 2px
        );
    background-size: 100% 100%, 100% 100%, 100% 3px;
    padding: 2rem 3rem;
    box-shadow: inset 0 0 80px rgba(139, 115, 85, 0.15), 0 0 20px rgba(0,0,0,0.15);
    border: 1px solid #b8a889;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #d4cdb8;
    background-image: 
        repeating-linear-gradient(
            90deg,
            transparent,
            transparent 1px,
            rgba(90,70,50,0.03) 1px,
            rgba(90,70,50,0.03) 2px
        );
    border-right: 5px double #2d241a;
    border-left: 3px solid #5a4a3a;
    padding: 1rem;
    box-shadow: inset -3px 0 8px rgba(0,0,0,0.2);
}

/* ORNAMENTAL HEADER */
.newspaper-header {
    text-align: center;
    border-top: 6px double #2d241a;
    border-bottom: 6px double #2d241a;
    padding: 2rem 1rem;
    margin-bottom: 2rem;
    background: linear-gradient(to bottom, #f5f0e6 0%, #e8e3d5 50%, #f5f0e6 100%);
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.1);
    position: relative;
}

.newspaper-header::before {
    content: "⚜";
    position: absolute;
    left: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 2.5rem;
    color: #5a4a3a;
    opacity: 0.4;
}

.newspaper-header::after {
    content: "⚜";
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 2.5rem;
    color: #5a4a3a;
    opacity: 0.4;
}

.newspaper-title {
    font-family: 'Old Standard TT', 'Playfair Display', serif;
    font-size: 4.2rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    margin: 0;
    color: #1a1410;
    text-shadow: 2px 2px 0px rgba(139, 115, 85, 0.2);
    text-transform: uppercase;
}

.newspaper-subtitle {
    font-size: 1rem;
    letter-spacing: 0.3em;
    margin-top: 0.8rem;
    font-variant: small-caps;
    color: #3d3228;
    font-weight: 600;
}

.newspaper-subtitle-small {
    font-size: 0.85rem;
    letter-spacing: 0.25em;
    margin-top: 0.5rem;
    font-variant: small-caps;
    color: #5a4a3a;
    font-weight: 500;
}

/* DATE LINE - Victorian style */
.dateline {
    text-align: center;
    font-size: 0.95rem;
    color: #3d3228;
    font-style: italic;
    margin-bottom: 2rem;
    font-variant: small-caps;
    letter-spacing: 0.1em;
    border-bottom: 1px solid #8b7355;
    padding-bottom: 0.8rem;
}

.dateline::before {
    content: "— ";
}

.dateline::after {
    content: " —";
}

/* HEADLINES - Industrial Revolution style */
.article-headline {
    font-family: 'Old Standard TT', serif;
    font-size: 2rem;
    font-weight: 700;
    text-transform: uppercase;
    border-top: 3px double #2d241a;
    border-bottom: 3px double #2d241a;
    margin: 2rem 0 1rem;
    padding: 0.8rem 0;
    text-align: center;
    letter-spacing: 0.15em;
    background: linear-gradient(to right, transparent 0%, #e8e3d5 20%, #e8e3d5 80%, transparent 100%);
}

.article-subhead {
    font-style: italic;
    color: #4a3f32;
    margin-bottom: 1.5rem;
    text-align: center;
    font-size: 1.05rem;
    font-variant: small-caps;
}

/* SCORE BOX - Victorian certificate style */
.credibility-box {
    border: 6px double #2d241a;
    padding: 2rem;
    background: linear-gradient(135deg, #f5f0e6 0%, #e8e3d5 50%, #f5f0e6 100%);
    text-align: center;
    margin: 2rem 0;
    position: relative;
    box-shadow: 
        inset 0 0 20px rgba(139, 115, 85, 0.2),
        0 4px 8px rgba(0,0,0,0.15);
}

.credibility-box::before {
    content: "";
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    bottom: 10px;
    border: 2px solid #8b7355;
    pointer-events: none;
}

.credibility-score {
    font-family: 'Old Standard TT', serif;
    font-size: 4rem;
    font-weight: 700;
    color: #2d241a;
    text-shadow: 3px 3px 0px rgba(139, 115, 85, 0.2);
    margin: 0.5rem 0;
}

.credibility-label {
    text-transform: uppercase;
    letter-spacing: 0.25em;
    font-size: 1rem;
    font-weight: 700;
    color: #3d3228;
    font-variant: small-caps;
    padding-left: 0.25em; /* Centers the text by balancing the trailing letter-spacing */
    display: block;
}

/* FLAGS / REPORT - Victorian list style */
.flag-item {
    padding: 0.7rem 0;
    border-bottom: 1px solid #8b7355;
    font-size: 0.95rem;
    line-height: 1.6;
}

.flag-item::before {
    content: "◆ ";
    color: #5a4a3a;
    margin-right: 0.5rem;
}

/* SIDEBAR ELEMENTS */
.sidebar-header {
    font-family: 'Old Standard TT', serif;
    font-size: 1.4rem;
    font-weight: 700;
    text-transform: uppercase;
    border-top: 3px double #2d241a;
    border-bottom: 3px double #2d241a;
    margin-bottom: 1.2rem;
    padding: 0.6rem 0;
    text-align: center;
    letter-spacing: 0.12em;
    color: #1a1410;
    background: rgba(232, 227, 213, 0.5);
}

/* CHECKLIST - Inspector's Manifest style */
.checklist-container {
    background-color: #f9f7f1;
    border: 3px double #5a4a3a;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
    position: relative;
    box-shadow: inset 0 0 15px rgba(139, 115, 85, 0.1);
}

.checklist-container::before {
    content: "OFFICIAL CRITERIA";
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: #d4cdb8;
    padding: 0 10px;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: #2d241a;
    font-weight: 700;
    border: 1px solid #5a4a3a;
}

.checklist-item {
    padding: 0.7rem 0.5rem;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    border-bottom: 1px dashed #b8a889;
    font-family: 'Libre Baskerville', serif;
    transition: background 0.2s;
}

.checklist-item:last-child {
    border-bottom: none;
}

.checklist-item:hover {
    background-color: rgba(139, 115, 85, 0.05);
}

.status-pass {
    font-weight: 700;
    color: #2e5a1c;
    font-family: 'Old Standard TT', serif;
    letter-spacing: 0.05em;
    border: 1px solid #2e5a1c;
    padding: 2px 6px;
    border-radius: 4px; /* Slight rounding for stamp look */
    font-size: 0.8rem;
    text-transform: uppercase;
}

.status-fail {
    font-weight: 700;
    color: #8b0000;
    font-family: 'Old Standard TT', serif; 
    text-decoration: none; /* Removed strikethrough for cleaner look */
    border: 1px solid #8b0000;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8rem;
    text-transform: uppercase;
}

.status-uncertain {
    font-weight: 700;
    color: #cf8a00;
    font-family: 'Old Standard TT', serif;
    border: 1px solid #cf8a00;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8rem;
    text-transform: uppercase;
}

.status-na {
    color: #666;
    font-style: italic;
    font-size: 0.8rem;
    font-family: 'Georgia', serif;
}

/* NEWS CARD STYLE */
.news-card {
    background: #fdfbf7;
    border: 1px solid #c9c0b1;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.08);
    position: relative;
    transition: transform 0.2s ease;
}

.news-card:hover {
    transform: translateY(-2px);
    box-shadow: 3px 3px 10px rgba(0,0,0,0.12);
}

.news-card-title {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: #2d241a;
    line-height: 1.3;
}

.news-card-source {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #8b7355;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid #e0d8c8;
    padding-bottom: 0.3rem;
    display: inline-block;
}

.news-card-snippet {
    font-family: 'Georgia', serif;
    font-size: 0.85rem;
    color: #4a3f32;
    line-height: 1.5;
    background: rgba(0,0,0,0.02);
    padding: 0.5rem;
    border-left: 3px solid #dcd5c5;
}

/* BUTTON - Victorian press style */
.stButton > button {
    background: linear-gradient(to bottom, #3d3228 0%, #2d241a 100%);
    color: #e8e3d5;
    border: 3px double #5a4a3a;
    font-family: 'Old Standard TT', serif;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.8rem 2.5rem;
    font-weight: 700;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
    font-size: 1rem;
}

.stButton > button:hover {
    background: linear-gradient(to bottom, #4a3f32 0%, #3d3228 100%);
    box-shadow: 0 2px 4px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.15);
}

/* TEXT AREA - aged paper style */
.stTextArea textarea {
    background-color: #f5f0e6 !important;
    border: 2px solid #8b7355 !important;
    color: #1a1410 !important;
    font-family: 'Libre Baskerville', serif !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1) !important;
}

/* PANELS - Official document style */
.paper-panel {
    background-color: #fdfbf7;
    border: 1px solid #c9c0b1;
    padding: 1.5rem;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    position: relative;
    height: 100%;
}

.paper-panel::before {
    content: "";
    position: absolute;
    top: 4px; left: 4px; right: 4px; bottom: 4px;
    border: 1px dashed #dcd5c5;
    pointer-events: none;
}

.report-text {
    font-family: 'Libre Baskerville', serif;
    font-size: 0.95rem;
    line-height: 1.7;
    color: #2d241a;
}

.verdict-stamp {
    display: inline-block;
    font-family: 'Old Standard TT', serif;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #5a4a3a;
    border-bottom: 1px solid #8b7355;
    padding-bottom: 0.2rem;
    margin-bottom: 0.8rem;
    font-size: 1.1rem;
}

/* TABS STYLING */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    background-color: transparent;
    border-bottom: 3px double #2d241a;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Old Standard TT', serif;
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5a4a3a;
    background-color: transparent;
    border: none;
    padding: 0.8rem 1.5rem;
}

.stTabs [aria-selected="true"] {
    color: #1a1410;
    border-bottom: 3px solid #2d241a;
    background-color: rgba(139, 115, 85, 0.1);
}

/* CRITICAL THINKING HUB STYLES */
.thinking-hub-container {
    background: linear-gradient(135deg, #f5f0e6 0%, #e8e3d5 100%);
    border: 4px double #2d241a;
    padding: 2rem;
    margin: 2rem 0;
    position: relative;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.thinking-hub-container::before {
    content: "";
    position: absolute;
    top: 8px;
    left: 8px;
    right: 8px;
    bottom: 8px;
    border: 1px dashed #8b7355;
    pointer-events: none;
}

.thinking-hub-title {
    font-family: 'Old Standard TT', serif;
    font-size: 2rem;
    font-weight: 700;
    text-transform: uppercase;
    text-align: center;
    letter-spacing: 0.2em;
    color: #1a1410;
    margin-bottom: 1rem;
    text-shadow: 1px 1px 0px rgba(139, 115, 85, 0.2);
}

.thinking-hub-intro {
    text-align: center;
    font-style: italic;
    color: #4a3f32;
    font-size: 1.05rem;
    margin-bottom: 2rem;
    padding: 0 2rem;
    line-height: 1.6;
}

.pointer-item {
    background: #fdfbf7;
    border-left: 5px solid #8b7355;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.08);
    position: relative;
}

.pointer-item::before {
    content: "❖";
    position: absolute;
    left: -15px;
    top: 50%;
    transform: translateY(-50%);
    color: #8b7355;
    font-size: 1.5rem;
    background: #e8e3d5;
    padding: 0 5px;
}

.pointer-text {
    font-family: 'Libre Baskerville', serif;
    font-size: 1rem;
    line-height: 1.7;
    color: #2d241a;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
current_date = datetime.now().strftime("%A, %B %d, %Y")

# Generate floating background divs
bg_html = "".join([f'<div class="floating-bg-{i}"></div>' for i in range(len(background_images))])

# Help Section Logic
if "show_help" not in st.session_state:
    st.session_state.show_help = False

def toggle_help():
    st.session_state.show_help = not st.session_state.show_help

# Header Layout with Help Button
col_head, col_btn = st.columns([0.9, 0.1])
with col_btn:
    st.button("❓", on_click=toggle_help, help="Open Bureau Guide")

if st.session_state.show_help:
    with st.expander("📜 BUREAU OPERATIONAL GUIDE", expanded=True):
        st.markdown("""
        <div style="font-family: 'Libre Baskerville', serif; color: #2d241a; font-size: 0.95rem;">
            <h4 style="font-family: 'Old Standard TT', serif; border-bottom: 1px solid #8b7355;">Operational Manual</h4>
            <ul style="list-style-type: square; padding-left: 1.5rem;">
                <li><strong>Verify Claim:</strong> Input text or URL to initiate the automated fact-checking protocol.</li>
                <li><strong>Credibility Score:</strong> Indicates the reliability of the claim based on our analysis.
                    <ul>
                        <li><span style="color: #2e5a1c; font-weight: bold;">VERIFIED (80%+)</span>: Highly reliable.</li>
                        <li><span style="color: #cf8a00; font-weight: bold;">QUESTIONABLE (40-80%)</span>: Exercise caution.</li>
                        <li><span style="color: #8b0000; font-weight: bold;">INCORRECT (<40%)</span>: Likely false.</li>
                    </ul>
                </li>
                <li><strong>Verification Checklist (Left Panel):</strong> A quick breakdown of key reliability indicators like tone, logic, and source validity.</li>
                <li><strong>Critical Thinking Hub:</strong> Provides perspectives to help you form your own independent judgment.</li>
                <li><strong>Supporting Articles:</strong> Consult these archived cross-references for further reading.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"""
{bg_html}
<div class="newspaper-header">
    <h1 class="newspaper-title">CrisisSafe</h1>
    <div class="newspaper-subtitle">Imperial Fact Verification Bureau</div>
    <div class="newspaper-subtitle-small">Est. MDCCCL • Team: Kernel Panic • Solo Submission</div>
</div>
<div class="dateline">{current_date}</div>
""", unsafe_allow_html=True)

# ---------------- INPUT ----------------
if "claim_input" not in st.session_state:
    st.session_state.claim_input = ""

st.markdown("""
<div class="article-headline">Submit Claim for Verification</div>
<div class="article-subhead">Enter the text or URL of the claim you wish to verify</div>
""", unsafe_allow_html=True)

user_input = st.text_area(
    "",
    placeholder="Paste claim text or article URL here...",
    height=120,
    label_visibility="collapsed",
    key="claim_input"
)

# ---------------- ANALYSIS ----------------
if st.button("VERIFY CLAIM", use_container_width=True):
    if user_input.strip():
        with st.spinner("Writing to the Imperial Archives..."):
            score, flags, ai_report, is_subjective, is_from_archive, checklist, related_articles, pointers = analyze_content(user_input)

        st.session_state.update({
            "score": score,
            "flags": flags,
            "ai_report": ai_report,
            "is_subjective": is_subjective,
            "is_from_archive": is_from_archive,
            "checklist": checklist,
            "related_articles": related_articles,
            "pointers": pointers
        })
    else:
        st.warning("Please enter content to verify.")

# ---------------- DISPLAY RESULTS ----------------
if "score" in st.session_state:
    score = st.session_state.score
    flags = st.session_state.flags
    ai_report = st.session_state.get("ai_report", "Analysis unavailable.")
    is_from_archive = st.session_state.get("is_from_archive", False)
    
    verdict = "VERIFIED" if score > 80 else "QUESTIONABLE" if score > 40 else "INCORRECT"

    if verdict == "QUESTIONABLE":
        display_score = "Questionable"
        display_label = ""
        score_style = "font-size: 3rem;"
    else:
        display_score = f"{score}%"
        display_label = verdict
        score_style = ""

    # Archive HTML Construction
    archive_html = ""
    if is_from_archive:
        archive_html = textwrap.dedent("""
        <div style="
            position: absolute;
            top: 0;
            right: 0;
            font-family: 'Old Standard TT', serif;
            font-size: 0.75rem;
            color: #8b7355;
            font-style: italic;
            padding: 4px 8px;
            background: rgba(232, 227, 213, 0.6);
            border-bottom: 1px solid #8b7355;
            border-left: 1px solid #8b7355;
        ">
            📦 Retrieved from Archive
        </div>""")

    # Main Credibility Box
    # Main Credibility Box
    # NOTE: We construct this as a single string without indentation to avoid Markdown treating it as a code block.
    # Four spaces of indentation triggers a code block in Markdown.
    html_content = (
        f'<div class="credibility-box">\n'
        f'{archive_html}\n'
        f'<div class="credibility-score" style="{score_style}">{display_score}</div>\n'
        f'<div class="credibility-label">{display_label}</div>\n'
        f'</div>'
    )
    
    st.markdown(html_content, unsafe_allow_html=True)

    # ---------------- TABS LAYOUT ----------------
    has_pointers = "pointers" in st.session_state and st.session_state.pointers
    
    if has_pointers:
        tab1, tab2 = st.tabs(["📋 Verification Report", "💡 Critical Thinking Hub"])
    else:
        tab1, = st.tabs(["📋 Verification Report"])
    
    with tab1:
        st.markdown("---")
        # --- VERIFICATION FLAGS ---
        st.markdown("<div class='article-headline'>Verification Flags</div>", unsafe_allow_html=True)
        
        flags_html = "<div class='paper-panel'>"
        if flags:
            for f in flags:
                flags_html += f"<div class='flag-item' style='border-bottom: 1px dashed #8b7355;'>{f}</div>"
        else:
            flags_html += "<div class='report-text' style='text-align: center; font-style: italic; color: #5a4a3a;'>No anomalies detected.<br>Content appears consistent with standard reporting.</div>"
        flags_html += "</div>"
        
        st.markdown(flags_html, unsafe_allow_html=True)

        # --- AI ANALYSIS ---
        st.markdown("<div class='article-headline' style='margin-top: 2rem;'>AI Analysis</div>", unsafe_allow_html=True)
        
        # Format AI Report
        formatted_report = ai_report
        if "VERDICT:" in ai_report:
            parts = ai_report.split("VERDICT:")
            # parts[0] is typically empty or includes preamble
            rest = parts[1] if len(parts) > 1 else ""
            
            if "EXPLANATION:" in rest:
                v_parts = rest.split("EXPLANATION:")
                verdict_text = v_parts[0].strip()
                explanation = v_parts[1].strip()
                
                formatted_report = f"<div style='text-align: center;'><div class='verdict-stamp'>{verdict_text}</div></div><div class='report-text'><strong>Analysis:</strong> {explanation}</div>"
            else:
                formatted_report = f"<div class='report-text'>{ai_report}</div>"
        else:
            formatted_report = f"<div class='report-text'>{ai_report}</div>"

        st.markdown(f"<div class='paper-panel'>{formatted_report}</div>", unsafe_allow_html=True)
        
        if "related_articles" in st.session_state and st.session_state.related_articles:
            count = len(st.session_state.related_articles)
            st.info(f"📚 {count} supporting articles found. View them in the sidebar 👈")
    
    # --- CRITICAL THINKING HUB TAB ---
    if has_pointers:
        with tab2:
            st.markdown(textwrap.dedent("""
            <div class="thinking-hub-container">
                <div class="thinking-hub-title">Critical Thinking Hub</div>
                <div class="thinking-hub-intro">
                    This topic involves subjectivity, complexity, or uncertainty. 
                    Consider these perspectives and questions before forming your final opinion.
                </div>
            """), unsafe_allow_html=True)
            
            for i, pointer in enumerate(st.session_state.pointers, 1):
                # Ensure no indentation in string content passed to markdown
                pointer_html = (
                    f'<div class="pointer-item">\n'
                    f'<div class="pointer-text">{pointer}</div>\n'
                    f'</div>'
                )
                st.markdown(pointer_html, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(textwrap.dedent("""
            <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: rgba(139, 115, 85, 0.1); border-radius: 8px;">
                <div style="font-family: 'Old Standard TT', serif; font-size: 1.1rem; color: #2d241a; font-style: italic;">
                    "The essence of the independent mind lies not in what it thinks, but in how it thinks."
                </div>
                <div style="font-size: 0.9rem; color: #5a4a3a; margin-top: 0.5rem;">— Christopher Hitchens</div>
            </div>
            """), unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<div class='sidebar-header'>Verification Checklist</div>", unsafe_allow_html=True)

    if "checklist" in st.session_state:
        checklist_labels = {
            "objective_language": "Objective Tone",
            "url_extraction": "Source Link",
            "no_panic_pattern": "Calm Punctuation",
            "no_shouting": "Standard Capitalization",
            "ai_verification": "AI Fact Check",
            "sanity_check": "Logic Sanity Check"
        }

        st.markdown("<div class='checklist-container'>", unsafe_allow_html=True)
        
        for key, value in st.session_state.checklist.items():
            label = checklist_labels.get(key, key.replace("_", " ").title())
            
            if value is True:
                status_html = "<span class='status-pass'>PASS</span>"
            elif value is False:
                status_html = "<span class='status-fail'>FAIL</span>"
            elif value == "uncertain":
                status_html = "<span class='status-uncertain'>UNCERTAIN</span>"
            else:
                status_html = "<span class='status-na'>N/A</span>"

            st.markdown(
                f"<div class='checklist-item'><span style='flex-grow:1'>{label}</span> {status_html}</div>",
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- EVIDENCE SIDEBAR ----------------
    if "related_articles" in st.session_state and st.session_state.related_articles:
        st.markdown("---")
        st.markdown("<div class='sidebar-header'>Supporting Articles</div>", unsafe_allow_html=True)
        
        for i, article in enumerate(st.session_state.related_articles):
            body_html = article.get('highlighted_body', article.get('body', ''))
            # Truncate content for card view
            clean_body = body_html[:200] + "..." if len(body_html) > 200 else body_html
            
            st.markdown(
                f'<div class="news-card">\n'
                f'    <div class="news-card-title">{article["title"]}</div>\n'
                f'    <div class="news-card-source">SOURCE: {article["url"][:30]}...</div>\n'
                f'    <div class="news-card-snippet">{clean_body}</div>\n'
                '</div>',
                unsafe_allow_html=True
            )
            
            # Using columns for better button placement
            col1, col2 = st.columns([1, 1])
            with col1:
                st.link_button("Read Full", article['url'])
            with col2:
                st.code(article['url'], language=None)
    else:
        if "checklist" not in st.session_state:
            st.markdown("<i>Run verification to see results.</i>", unsafe_allow_html=True)