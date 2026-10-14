import streamlit as st

STAR_SVG = """<svg viewBox="0 0 24 24" fill="none" style="width:16px; height:16px;">
<path d="M12 2.5l2.9 6.2 6.6.7-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6L2.5 9.4l6.6-.7L12 2.5z"
fill="#7FA3EC"/></svg>"""

THEME_CSS = """
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
        color: #ffffff;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: var(--sp-4); padding-bottom: var(--sp-6); max-width: 1050px; }

    /* ============ Typography ============ */
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-display) !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    .page-title {
        font-family: var(--font-display);
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .page-title .accent {
        background: linear-gradient(100deg, var(--blue-300) 10%, #ffffff 50%, var(--blue-300) 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .page-sub {
        color: rgba(255,255,255,0.74);
        font-size: var(--fs-base);
        font-weight: 500;
        margin-bottom: var(--sp-5);
        line-height: 1.5;
    }

    /* ============ Navbar ============ */
    .nav-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 0 var(--sp-4);
        margin-bottom: var(--sp-3);
        border-bottom: 1px solid rgba(255,255,255,0.1);
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

    .active-badge {
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
        border-radius: var(--r-pill); padding: 4px 14px;
        font-size: var(--fs-xs); font-weight: 600; color: #ffffff;
    }
    .active-badge .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.25);
    }

    /* ============ Metric Cards ============ */
    div[data-testid="stMetric"] {
        background: var(--paper-0) !important;
        border: 1.5px solid var(--border-1) !important;
        border-radius: var(--r-lg) !important;
        padding: 14px 18px !important;
        box-shadow: 0 10px 24px -10px rgba(0,0,0,0.25) !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: var(--ink-500) !important;
        font-weight: 700 !important;
        font-size: var(--fs-xs) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.4px !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--ink-900) !important;
        font-family: var(--font-display) !important;
        font-weight: 700 !important;
        font-size: 1.45rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }

    /* ============ White Container Cards ============ */
    .white-card {
        background: var(--paper-0);
        border: 1.5px solid var(--border-1);
        border-radius: var(--r-xl);
        box-shadow: 0 2px 0 var(--border-1), 0 16px 32px -24px rgba(20,32,62,0.18);
        padding: var(--sp-6) var(--sp-7);
        color: var(--ink-900);
        margin-bottom: var(--sp-5);
    }
    .white-card h1, .white-card h2, .white-card h3, .white-card h4 {
        color: var(--ink-900) !important;
    }
    .white-card p, .white-card span {
        color: var(--ink-700);
    }

    /* ============ Expanders & Containers ============ */
    div[data-testid="stExpander"] {
        background: var(--paper-0) !important;
        border: 1.5px solid var(--border-1) !important;
        border-radius: var(--r-lg) !important;
        box-shadow: 0 10px 25px -10px rgba(0,0,0,0.15) !important;
        color: var(--ink-900) !important;
        margin-bottom: var(--sp-4) !important;
    }
    div[data-testid="stExpander"] details {
        color: var(--ink-900) !important;
    }
    div[data-testid="stExpander"] summary {
        color: var(--ink-900) !important;
        font-weight: 700 !important;
        font-family: var(--font-display) !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        color: var(--ink-700) !important;
    }

    /* ============ Tabs ============ */
    div[data-baseweb="tab-list"] {
        gap: 6px !important;
        border-bottom: 2px solid rgba(255,255,255,0.12) !important;
        padding-bottom: 2px !important;
        margin-bottom: var(--sp-5) !important;
    }
    button[data-baseweb="tab"] {
        background: rgba(255,255,255,0.06) !important;
        color: rgba(255,255,255,0.72) !important;
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        font-size: var(--fs-sm) !important;
        border-radius: var(--r-md) var(--r-md) 0 0 !important;
        padding: 9px 18px !important;
        transition: all 0.18s ease !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-bottom: none !important;
    }
    button[data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.12) !important;
        color: #ffffff !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background: var(--blue-700) !important;
        border-color: var(--blue-300) !important;
        border-bottom: 3px solid var(--blue-300) !important;
    }

    /* ============ Primary Buttons ============ */
    div.stButton > button[kind="primary"] {
        position: relative; overflow: hidden;
        background: linear-gradient(135deg, var(--blue-700) 0%, var(--blue-500) 100%) !important;
        border: none !important;
        border-bottom: 4px solid #10265C !important;
        border-radius: var(--r-md) !important;
        padding: var(--sp-3) var(--sp-4) !important;
        font-weight: 700 !important; font-size: var(--fs-md) !important;
        color: #ffffff !important;
        transition: transform 0.08s ease, border-bottom-width 0.08s ease !important;
        box-shadow: 0 4px 14px rgba(47,95,214,0.3) !important;
    }
    div.stButton > button[kind="primary"]::after {
        content: ""; position: absolute; top: 0; left: -60%; width: 40%; height: 100%;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.28), transparent);
        transform: skewX(-20deg);
        transition: left 0.55s ease;
    }
    div.stButton > button[kind="primary"]:hover::after { left: 130%; }
    div.stButton > button[kind="primary"]:hover { transform: translateY(1px); filter: brightness(1.05); }
    div.stButton > button[kind="primary"]:active { border-bottom-width: 1px !important; transform: translateY(3px); }

    /* ============ Secondary Buttons ============ */
    div.stButton > button:not([kind="primary"]) {
        background: var(--paper-0) !important;
        border: 1.5px solid var(--border-2) !important;
        border-radius: var(--r-md) !important;
        padding: var(--sp-3) var(--sp-4) !important;
        font-weight: 700 !important; font-size: var(--fs-sm) !important;
        color: var(--ink-700) !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
    }
    div.stButton > button:not([kind="primary"]):hover {
        border-color: var(--blue-500) !important;
        color: var(--blue-700) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.12) !important;
    }

    /* ============ DataFrames ============ */
    div[data-testid="stDataFrame"] {
        background: var(--paper-0) !important;
        border-radius: var(--r-md) !important;
        border: 1px solid var(--border-2) !important;
        padding: 4px !important;
        box-shadow: 0 10px 25px -10px rgba(0,0,0,0.2) !important;
    }

    /* ============ Form Inputs ============ */
    .stTextInput > div > div > input,
    .stTextArea textarea {
        background: var(--paper-0) !important;
        border: 1.5px solid var(--border-2) !important;
        border-radius: var(--r-md) !important;
        color: var(--ink-900) !important;
        font-weight: 500 !important;
    }
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: rgba(255,255,255,0.85) !important;
        font-weight: 600 !important;
        font-size: var(--fs-sm) !important;
    }
    div[data-baseweb="select"] > div {
        border-radius: var(--r-md) !important;
        background: var(--paper-0) !important;
        color: var(--ink-900) !important;
    }

    /* ============ Alert Boxes ============ */
    div[data-testid="stAlert"] {
        border-radius: var(--r-md) !important;
        font-weight: 500 !important;
    }

    /* ============ Deep Dive Feature Cards ============ */
    .feature-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        border-radius: var(--r-lg);
        padding: 18px 16px;
        text-align: center;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: var(--blue-300);
        background: rgba(255, 255, 255, 0.14);
        box-shadow: 0 12px 28px rgba(47, 95, 214, 0.3);
    }
    .feature-card .card-icon {
        font-size: 2.1rem;
        margin-bottom: 6px;
    }
    .feature-card .card-title {
        font-family: var(--font-display);
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 4px;
        color: #ffffff;
    }
    .feature-card .card-desc {
        font-size: 0.78rem;
        color: rgba(255, 255, 255, 0.75);
        line-height: 1.35;
        text-align: center;
    }
</style>
"""


def apply_theme():
    """Injects the Rating Ink v2 design system into the active Streamlit page."""
    if hasattr(st, "html"):
        st.html(THEME_CSS)
    else:
        st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_page_header(title="", subtitle="", icon="⭐", *args, **kwargs):
    """
    Renders the consistent top navbar, active dataset badge, and stylized page header.
    """
    if 'icon' in kwargs:
        icon = kwargs.get('icon', icon)
    if 'title' in kwargs:
        title = kwargs.get('title', title)
    if 'subtitle' in kwargs:
        subtitle = kwargs.get('subtitle', subtitle)
        
    apply_theme()
    
    dataset_name = st.session_state.get('dataset_name', None)
    if dataset_name:
        badge_html = f'<div class="active-badge"><div class="dot"></div><span>{dataset_name}</span></div>'
    else:
        badge_html = '<div class="active-badge" style="opacity:0.75;"><span style="font-size:0.75rem;">No active file</span></div>'

    clean_star = STAR_SVG.strip()
    header_html = (
        f'<div class="nav-header">'
        f'<div class="brand"><span class="pulse-star">{clean_star}</span><span>Review<span style="color:var(--blue-300);">Pulse</span></span></div>'
        f'{badge_html}'
        f'</div>'
        f'<div class="page-title">{icon} <span class="accent">{title}</span></div>'
        f'<div class="page-sub">{subtitle}</div>'
    )

    if hasattr(st, "html"):
        st.html(header_html)
    else:
        st.markdown(header_html, unsafe_allow_html=True)


def render_feature_card(icon, title, desc):
    """Renders a feature deep-dive card cleanly without markdown indentation errors."""
    card_html = (
        f'<div class="feature-card">'
        f'<div>'
        f'<div class="card-icon">{icon}</div>'
        f'<div class="card-title">{title}</div>'
        f'<div class="card-desc">{desc}</div>'
        f'</div>'
        f'</div>'
    )
    if hasattr(st, "html"):
        st.html(card_html)
    else:
        st.markdown(card_html, unsafe_allow_html=True)


def render_no_data_warning(feature_name="this analysis"):
    """
    Renders a unified prompt when no dataset has been uploaded yet,
    with an immediate 1-click sample dataset loader.
    """
    st.info(f"No active dataset found. Upload a review file or load our sample reviews to explore {feature_name}.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🚀 Load Sample Reviews", use_container_width=True, key=f"no_data_btn_{feature_name}"):
            with st.spinner("Analyzing sample dataset... ☕"):
                import analyzer_service
                s_df = analyzer_service.get_sample_dataset()
                res = analyzer_service.run_analysis_local(s_df, "Review_Text", "Date")
                st.session_state['results'] = res
                st.session_state['dataset_name'] = "Sample E-Commerce Reviews"
                st.rerun()
    with col2:
        if st.button("📁 Go to Upload Page", use_container_width=True, key=f"go_home_{feature_name}"):
            st.switch_page("app.py")


def style_chart(fig, height=None):
    """
    Applies Rating Ink v2 dark theme to Plotly figures for seamless visual integration.
    """
    if fig is None:
        return fig
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.04)",
        font=dict(color="#ffffff", family="Inter, Segoe UI, sans-serif"),
        title_font=dict(color="#ffffff", family="Space Grotesk, sans-serif", size=16),
        legend=dict(font=dict(color="#ffffff")),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)")
    return fig

