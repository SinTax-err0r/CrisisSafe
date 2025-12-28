import streamlit as st
from rules import analyze_content
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CrisisSafe",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- VICTORIAN IMPERIAL NEWSPAPER CSS ----------------
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
    font-size: 0.75rem;
    letter-spacing: 0.3em;
    margin-top: 0.6rem;
    font-variant: small-caps;
    color: #3d3228;
    font-weight: 600;
}

/* DATE LINE - Victorian style */
.dateline {
    text-align: center;
    font-size: 0.8rem;
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
}

.checklist-item {
    border-bottom: 1px solid #8b7355;
    padding: 0.8rem 0;
    font-size: 0.9rem;
}

.checklist-item::before {
    content: "► ";
    color: #5a4a3a;
    margin-right: 0.4rem;
}

.status-pass {
    font-weight: 700;
    color: #1a5a1a;
}

.status-fail {
    font-weight: 700;
    color: #5a1a1a;
    text-decoration: line-through;
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
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
current_date = datetime.now().strftime("%A, %B %d, %Y")

st.markdown(f"""
<div class="newspaper-header">
    <h1 class="newspaper-title">CrisisSafe</h1>
    <div class="newspaper-subtitle">Imperial Fact Verification Bureau</div>
    <div class="newspaper-subtitle" style="font-size:0.65rem;">Est. MDCCCL • Team: Kernel Panic • Solo Submission</div>
</div>
<div class="dateline">{current_date}</div>
""", unsafe_allow_html=True)

# ---------------- INPUT ----------------
st.markdown("""
<div class="article-headline">Submit Claim for Verification</div>
<div class="article-subhead">Enter the text or URL of the claim you wish to verify</div>
""", unsafe_allow_html=True)

user_input = st.text_area(
    "",
    placeholder="Paste claim text or article URL here...",
    height=120,
    label_visibility="collapsed"
)

# ---------------- ANALYSIS ----------------
if st.button("VERIFY CLAIM", use_container_width=True):
    if user_input.strip():
        with st.spinner("Analyzing claim..."):
            score, flags, ai_report, is_subjective, is_from_archive, checklist = analyze_content(user_input)

        st.session_state.update({
            "score": score,
            "flags": flags,
            "ai_report": ai_report,
            "is_subjective": is_subjective,
            "is_from_archive": is_from_archive,
            "checklist": checklist
        })

        verdict = "VERIFIED" if score > 80 else "QUESTIONABLE" if score > 40 else "UNVERIFIED"

        st.markdown(f"""
        <div class="credibility-box">
            <div class="credibility-score">{score}%</div>
            <div class="credibility-label">{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='article-headline'>Verification Flags</div>", unsafe_allow_html=True)
            if flags:
                for f in flags:
                    st.markdown(f"<div class='flag-item'>{f}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<i>No flags detected.</i>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='article-headline'>AI Analysis</div>", unsafe_allow_html=True)
            st.markdown(ai_report or "<i>AI analysis unavailable.</i>", unsafe_allow_html=True)

    else:
        st.warning("Please enter content to verify.")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<div class='sidebar-header'>Verification Checklist</div>", unsafe_allow_html=True)

    if "checklist" in st.session_state:
        for key, value in st.session_state.checklist.items():
            status = "PASS" if value is True else "FAIL" if value is False else "N/A"
            cls = "status-pass" if value else "status-fail"
            st.markdown(
                f"<div class='checklist-item'><span class='{cls}'>{key.upper()}: {status}</span></div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown("<i>Run verification to see results.</i>", unsafe_allow_html=True)