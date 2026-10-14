import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ReviewPulse | AI Review Intelligence", layout="wide", page_icon="⭐")

# ------------------------------------------------------------------
# DESIGN SYSTEM — "Rating Ink v2"
# The hero is a tilted stack of real product artifacts (a review
# card + a rating-distribution mini chart) instead of abstract blobs,
# a scrolling ticker of what the tool surfaces, and one signature
# animated moment: stars filling in like a rating being cast.
# ------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --blue-900:    #14203E;
        --blue-700:    #1E3A72;
        --blue-500:    #2F5FD6;
        --blue-300:    #7FA3EC;
        --blue-soft:   #E7EEFC;
        --sage:        #4F8B6E;
        --sage-soft:   #E6F1EA;
        --coral:       #E4573D;
        --coral-soft:  #FBE5E0;

        --ink-900: #16203D;
        --ink-700: #3C4566;
        --ink-500: #6C7391;
        --ink-400: #8B92AC;
        --ink-300: #B4B9CE;

        --paper-0: #FFFFFF;
        --paper-1: #F5F7FC;
        --border-1: #E7EAF3;
        --border-2: #DCE1EF;

        --sp-1: 4px;  --sp-2: 8px;  --sp-3: 10px; --sp-4: 14px;
        --sp-5: 18px; --sp-6: 22px; --sp-7: 28px; --sp-8: 36px;

        --r-sm: 8px; --r-md: 12px; --r-lg: 18px; --r-xl: 24px; --r-pill: 999px;

        --fs-xs: 0.76rem; --fs-sm: 0.86rem; --fs-base: 0.95rem; --fs-md: 1rem;
        --fs-lg: 1.15rem; --fs-xl: 1.5rem; --fs-2xl: 2.15rem;

        --font-display: 'Space Grotesk', sans-serif;
        --font-body: 'Inter', 'Segoe UI', system-ui, sans-serif;
    }

    html, body, [class*="css"] { font-family: var(--font-body); }

    .stApp {
        background: var(--blue-900);
        background-image:
            radial-gradient(circle at 15% -10%, rgba(127,163,236,0.28) 0%, transparent 45%),
            radial-gradient(circle at 100% 30%, rgba(127,163,236,0.14) 0%, transparent 50%),
            linear-gradient(180deg, var(--blue-900) 0%, var(--blue-700) 100%);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: var(--sp-4); padding-bottom: var(--sp-5); max-width: 900px; }

    /* ============ Navbar ============ */
    .navbar {
        display: flex; align-items: center; justify-content: center;
        gap: var(--sp-2);
        padding: var(--sp-2) 0 var(--sp-4);
    }
    .brand {
        font-family: var(--font-display); font-size: 1.15rem; font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.3px;
        display: flex; align-items: center; gap: 7px;
    }
    .brand .pulse-star { display: inline-flex; animation: twinkle 3.2s ease-in-out infinite; }
    @keyframes twinkle {
        0%, 100% { transform: scale(1) rotate(0deg); opacity: 1; }
        50% { transform: scale(1.2) rotate(8deg); opacity: 0.8; }
    }

    /* ============ Hero ============ */
    .hero { text-align: center; padding: var(--sp-2) var(--sp-4) var(--sp-6); position: relative; }
    .hero-title {
        font-family: var(--font-display); font-weight: 700;
        font-size: var(--fs-2xl); line-height: 1.14; letter-spacing: -0.5px;
        color: #ffffff;
        max-width: 560px; margin: 0 auto var(--sp-3);
    }
    .hero-title .accent {
        background: linear-gradient(100deg, var(--blue-300) 10%, #ffffff 50%, var(--blue-300) 90%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        color: rgba(255,255,255,0.72); font-size: var(--fs-sm); font-weight: 500;
        max-width: 440px; margin: 0 auto;
        line-height: 1.5;
    }

    /* ============ Hero mockup: layered review-card + rating chart ============ */
    .mockup-stage { position: relative; height: 168px; max-width: 480px; margin: var(--sp-6) auto 0; }
    .mock-card {
        position: absolute; background: var(--paper-0); border-radius: var(--r-lg);
        box-shadow: 0 24px 40px -18px rgba(0,0,0,0.45);
        text-align: left;
    }
    .mock-review {
        width: 280px; left: 0; top: 6px; padding: var(--sp-4);
        transform: rotate(-5deg);
        animation: floatA 6s ease-in-out infinite;
    }
    .mock-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
    .mock-avatar {
        width: 26px; height: 26px; border-radius: 50%;
        background: linear-gradient(135deg, var(--blue-500), var(--blue-300));
        flex-shrink: 0;
    }
    .mock-name { font-weight: 700; font-size: 0.82rem; color: var(--ink-900); }
    .mock-stars { display: flex; gap: 2px; margin-bottom: 6px; }
    .mock-stars svg { width: 13px; height: 13px; animation: starPop 0.45s cubic-bezier(.2,1.4,.4,1) both; }
    .mock-stars svg:nth-child(1) { animation-delay: 0.5s; }
    .mock-stars svg:nth-child(2) { animation-delay: 0.6s; }
    .mock-stars svg:nth-child(3) { animation-delay: 0.7s; }
    .mock-stars svg:nth-child(4) { animation-delay: 0.8s; }
    .mock-stars svg:nth-child(5) { animation-delay: 0.9s; }
    .mock-text { font-size: 0.78rem; color: var(--ink-700); line-height: 1.4; margin-bottom: 8px; }
    .mock-tag {
        display: inline-flex; align-items: center; gap: 4px;
        background: var(--sage-soft); color: var(--sage);
        border-radius: var(--r-pill); padding: 2px 9px; font-size: 0.7rem; font-weight: 700;
    }
    .mock-chart {
        width: 200px; right: 0; bottom: 0; padding: var(--sp-4);
        transform: rotate(4deg);
        animation: floatB 7s ease-in-out infinite;
    }
    .mock-chart .mc-label { font-size: 0.72rem; font-weight: 700; color: var(--ink-500); margin-bottom: 10px; }
    .mc-bars { display: flex; align-items: flex-end; gap: 6px; height: 56px; }
    .mc-bar { flex: 1; border-radius: 4px 4px 0 0; background: var(--blue-500); transform-origin: bottom; animation: growBar 0.9s cubic-bezier(.2,1,.3,1) both; }
    .mc-bar:nth-child(1) { height: 30%; background: var(--coral); opacity: 0.55; animation-delay: 0.2s; }
    .mc-bar:nth-child(2) { height: 18%; background: var(--coral); opacity: 0.4; animation-delay: 0.3s; }
    .mc-bar:nth-child(3) { height: 40%; background: var(--blue-300); animation-delay: 0.4s; }
    .mc-bar:nth-child(4) { height: 68%; background: var(--blue-500); animation-delay: 0.5s; }
    .mc-bar:nth-child(5) { height: 100%; background: var(--blue-700); animation-delay: 0.6s; }

    @keyframes floatA {
        0%, 100% { transform: rotate(-5deg) translateY(0); }
        50% { transform: rotate(-5deg) translateY(-7px); }
    }
    @keyframes floatB {
        0%, 100% { transform: rotate(4deg) translateY(0); }
        50% { transform: rotate(4deg) translateY(6px); }
    }
    @keyframes starPop {
        0% { transform: scale(0) rotate(-25deg); opacity: 0; }
        70% { transform: scale(1.25) rotate(6deg); opacity: 1; }
        100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    @keyframes growBar {
        0% { transform: scaleY(0); }
        100% { transform: scaleY(1); }
    }

    /* ============ Ticker ============ */
    .ticker-wrap {
        overflow: hidden; max-width: 100%; margin: var(--sp-6) auto 0; padding-bottom: 2px;
        -webkit-mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
        mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
    }
    .ticker-track {
        display: flex; gap: var(--sp-2); width: max-content;
        animation: scrollTicker 22s linear infinite;
    }
    .ticker-chip {
        display: flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.94); border: 1px solid rgba(255,255,255,0.5);
        border-radius: var(--r-pill); padding: 6px 13px;
        font-size: var(--fs-xs); font-weight: 700; color: var(--blue-700); white-space: nowrap;
    }
    @keyframes scrollTicker {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    /* ============ Card ============ */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stFileUploader"]) {
        background: var(--paper-0) !important;
        border: 1.5px solid var(--border-1) !important;
        border-radius: var(--r-xl) !important;
        box-shadow: 0 2px 0 var(--border-1), 0 16px 32px -24px rgba(20,32,62,0.18);
        padding: var(--sp-6) var(--sp-7) var(--sp-5) !important;
        margin: var(--sp-6) 0 var(--sp-4) !important;
    }
    .card-eyebrow {
        display: inline-flex; align-items: center; gap: 6px;
        background: var(--blue-soft); color: var(--blue-700);
        border-radius: var(--r-pill); padding: 3px 11px;
        font-size: var(--fs-xs); font-weight: 700;
        margin-bottom: var(--sp-2);
    }
    .card-title {
        font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700;
        color: var(--ink-900);
        margin-bottom: 2px;
    }
    .card-subtitle {
        color: var(--ink-500);
        font-size: var(--fs-sm);
        font-weight: 500;
        margin-bottom: var(--sp-4);
        max-width: 480px;
    }
    .upload-hint {
        color: var(--ink-400); font-size: var(--fs-xs); font-weight: 600;
        margin-top: 3px; margin-bottom: var(--sp-2);
    }
    .section-label {
        font-family: var(--font-display); font-weight: 600; font-size: var(--fs-sm);
        color: var(--ink-900); margin-bottom: var(--sp-1);
    }

    /* ============ Inputs ============ */
    .stTextInput label, .stFileUploader label, .stSelectbox label {
        color: var(--ink-700) !important; font-weight: 700 !important; font-size: var(--fs-sm) !important;
    }
    .stTextInput > div > div > input {
        background: var(--blue-soft) !important;
        border: 2px dashed var(--blue-300) !important;
        border-radius: var(--r-lg) !important;
        color: var(--ink-700) !important;
        padding: var(--sp-3) var(--sp-4) !important;
        font-weight: 600 !important;
        height: 78px !important;
        transition: border-color 0.15s ease, background 0.15s ease;
    }
    .stTextInput > div > div > input:focus {
        border-style: solid !important;
        box-shadow: 0 0 0 4px rgba(47,95,214,0.18) !important;
    }
    section[data-testid="stFileUploaderDropzone"] {
        background: var(--blue-soft) !important;
        border: 2px dashed var(--blue-300) !important;
        border-radius: var(--r-lg) !important;
        transition: border-color 0.15s ease, transform 0.15s ease;
    }
    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--blue-500) !important;
    }
    div[data-baseweb="select"] > div {
        border-radius: var(--r-md) !important;
        border-color: var(--border-2) !important;
    }

    /* ============ Primary button — shine sweep on hover ============ */
    div.stButton > button[kind="primary"] {
        position: relative; overflow: hidden;
        background: linear-gradient(135deg, var(--blue-700) 0%, var(--blue-500) 100%);
        border: none;
        border-bottom: 4px solid #10265C;
        border-radius: var(--r-md);
        padding: var(--sp-3) var(--sp-4);
        font-weight: 700; font-size: var(--fs-md);
        color: #ffffff;
        transition: transform 0.08s ease, border-bottom-width 0.08s ease;
    }
    div.stButton > button[kind="primary"]::after {
        content: ""; position: absolute; top: 0; left: -60%; width: 40%; height: 100%;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.28), transparent);
        transform: skewX(-20deg);
        transition: left 0.55s ease;
    }
    div.stButton > button[kind="primary"]:hover::after { left: 130%; }
    div.stButton > button[kind="primary"]:hover { transform: translateY(1px); }
    div.stButton > button[kind="primary"]:active { border-bottom-width: 1px; transform: translateY(3px); }

    div.stButton > button:not([kind="primary"]) {
        background: var(--paper-0);
        border: 1.5px solid var(--border-2);
        border-radius: var(--r-md);
        padding: var(--sp-3) var(--sp-4);
        font-weight: 700; font-size: var(--fs-sm);
        color: var(--ink-700);
        transition: border-color 0.15s ease, color 0.15s ease, transform 0.08s ease;
    }
    div.stButton > button:not([kind="primary"]):hover {
        border-color: var(--blue-500);
        color: var(--blue-700);
        transform: translateY(-1px);
    }

    .footnote { text-align: center; color: rgba(255,255,255,0.55); font-size: var(--fs-xs); font-weight: 500; margin-top: var(--sp-4); }

    .active-banner {
        background: var(--sage-soft);
        border: 1.5px solid #D3E7DA;
        border-radius: var(--r-lg);
        padding: var(--sp-4) var(--sp-5);
        margin-bottom: var(--sp-3);
        display: flex; align-items: center; gap: var(--sp-3);
    }
    .active-banner .badge-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--sage); flex-shrink: 0; box-shadow: 0 0 0 4px rgba(79,139,110,0.18); }
    .active-banner .label { font-size: var(--fs-xs); font-weight: 700; color: var(--sage); margin-bottom: 2px; }
    .active-banner .name { font-family: var(--font-display); font-weight: 700; font-size: var(--fs-lg); color: var(--ink-900); }
</style>
""", unsafe_allow_html=True)

STAR_SVG = """<svg viewBox="0 0 24 24" fill="none">
<path d="M12 2.5l2.9 6.2 6.6.7-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6L2.5 9.4l6.6-.7L12 2.5z"
fill="#2F5FD6"/></svg>"""

TICKER_ITEMS = [
    "⭐ Rating trends", "💬 Positive themes", "⚠️ Pain points", "📈 Sentiment over time",
    "🔍 Keyword clusters", "🎯 Auto-summaries",
]

# ------------------------------------------------------------------
# NAVBAR
# ------------------------------------------------------------------
navbar_html = f"""<div class="navbar"><div class="brand"><span class="pulse-star">{STAR_SVG}</span>Review<span style="color:var(--blue-300)">Pulse</span></div></div>"""
if hasattr(st, "html"):
    st.html(navbar_html)
else:
    st.markdown(navbar_html, unsafe_allow_html=True)

import analyzer_service

# ------------------------------------------------------------------
# 1. FILE UPLOAD SECTION
# ------------------------------------------------------------------
if 'results' not in st.session_state:

    ticker_html = "".join(f'<div class="ticker-chip">{item}</div>' for item in (TICKER_ITEMS * 2))

    hero_html = f"""<div class="hero">
        <div class="hero-title">Turn a pile of reviews into <span class="accent">a story worth reading</span></div>
        <div class="hero-sub">Upload a spreadsheet of customer reviews and get sentiment, themes, and trends back in seconds.</div>
        <div class="mockup-stage">
            <div class="mock-card mock-review">
                <div class="mock-row">
                    <div class="mock-avatar"></div>
                    <div class="mock-name">Jordan M.</div>
                </div>
                <div class="mock-stars">{STAR_SVG}{STAR_SVG}{STAR_SVG}{STAR_SVG}{STAR_SVG}</div>
                <div class="mock-text">"Absolutely love the quality — arrived early and packaging was great."</div>
                <div class="mock-tag">😊 Positive</div>
            </div>
            <div class="mock-card mock-chart">
                <div class="mc-label">Rating distribution</div>
                <div class="mc-bars">
                    <div class="mc-bar"></div><div class="mc-bar"></div><div class="mc-bar"></div>
                    <div class="mc-bar"></div><div class="mc-bar"></div>
                </div>
            </div>
        </div>
        <div class="ticker-wrap"><div class="ticker-track">{ticker_html}</div></div>
    </div>"""
    if hasattr(st, "html"):
        st.html(hero_html)
    else:
        st.markdown(hero_html, unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_file = st.file_uploader("Your review file", type=["csv", "xlsx", "xls", "tsv"])
            st.markdown('<p class="upload-hint">200MB per file • CSV, XLSX, XLS, TSV</p>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="height:26px"></div>', unsafe_allow_html=True)
            if st.button("⚡ Load Sample Reviews", use_container_width=True, help="Load a pre-built rich consumer review dataset to test immediately"):
                with st.spinner("Analyzing sample dataset..."):
                    try:
                        sample_df = analyzer_service.get_sample_dataset()
                        res = analyzer_service.run_analysis_local(sample_df, "Review_Text", "Date")
                        st.session_state['results'] = res
                        st.session_state['dataset_name'] = "Sample E-Commerce Reviews"
                        st.success("Sample dataset loaded! Redirecting to Dashboard...")
                    except Exception as e:
                        st.error(f"Error loading sample dataset: {e}")
                if 'results' in st.session_state:
                    st.switch_page("pages/0_📊_Dashboard.py")

        # Column configuration
        text_column = "Review Text"
        date_column = "Date"

        if uploaded_file is not None:
            try:
                file_bytes = uploaded_file.getvalue()
                preview_df = analyzer_service.read_file_into_df(file_bytes, uploaded_file.name)
                detected_text, detected_date = analyzer_service.detect_columns(preview_df)
                cols = list(preview_df.columns)

                st.markdown('<div class="section-label">Configure columns</div>', unsafe_allow_html=True)
                c_text, c_date = st.columns(2)
                with c_text:
                    text_idx = cols.index(detected_text) if detected_text in cols else 0
                    text_column = st.selectbox("Review text column (required)", options=cols, index=text_idx)
                with c_date:
                    date_options = ["None"] + cols
                    date_idx = date_options.index(detected_date) if detected_date in date_options else 0
                    selected_date = st.selectbox("Date column (optional)", options=date_options, index=date_idx)
                    date_column = None if selected_date == "None" else selected_date

                with st.expander(f"Preview uploaded data ({len(preview_df)} rows)", expanded=False):
                    st.dataframe(preview_df.head(5), use_container_width=True)
            except Exception as e:
                st.warning(f"Could not preview file: {e}")

    if st.button("✨  Get My Insights", type="primary", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("Reading your reviews and generating insights... this only takes a moment."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    results = analyzer_service.run_analysis(
                        file_bytes=file_bytes,
                        filename=uploaded_file.name,
                        text_col=text_column,
                        date_col=date_column
                    )
                    st.session_state['results'] = results
                    st.session_state['dataset_name'] = uploaded_file.name
                    st.success("All done! Taking you to your dashboard...")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
        else:
            with st.spinner("No file uploaded — loading sample review dataset for you!"):
                try:
                    sample_df = analyzer_service.get_sample_dataset()
                    results = analyzer_service.run_analysis_local(sample_df, "Review_Text", "Date")
                    st.session_state['results'] = results
                    st.session_state['dataset_name'] = "Sample E-Commerce Reviews"
                    st.success("Sample reviews loaded! Taking you to your dashboard...")
                except Exception as e:
                    st.error(f"Could not load sample reviews: {e}")

        if 'results' in st.session_state:
            st.switch_page("pages/0_📊_Dashboard.py")

    st.markdown('<p class="footnote">Your data is processed securely and never shared</p>', unsafe_allow_html=True)

else:
    active_html = f"""<div class="active-banner">
        <div class="badge-dot"></div>
        <div>
            <div class="label">Active dataset</div>
            <div class="name">{st.session_state.get('dataset_name', 'Uploaded Dataset')}</div>
        </div>
    </div>"""
    if hasattr(st, "html"):
        st.html(active_html)
    else:
        st.markdown(active_html, unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📊 Go to Dashboard Overview", type="primary", use_container_width=True):
            st.switch_page("pages/0_📊_Dashboard.py")
    with col_b:
        if st.button("🔄 Upload New File", use_container_width=True):
            del st.session_state['results']
            if 'dataset_name' in st.session_state:
                del st.session_state['dataset_name']
            st.rerun()