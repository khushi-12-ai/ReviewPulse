import streamlit as st
import pandas as pd
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

import analyzer_service
import ui_theme

st.set_page_config(page_title="Text Cleaning | ReviewPulse", page_icon="🧹", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Text Preprocessing & Cleaning",
    subtitle="Standardizes raw unstructured customer reviews by stripping HTML tags, URLs, special symbols, and normalizing case for maximum NLP accuracy.",
    icon="🧹"
)

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live Text Cleaning Sandbox (Test any raw text)", expanded=False):
    sample_raw = st.text_area(
        "Enter dirty text to test cleaning pipeline:",
        value="<p>Check out our website at https://gadgets.com! The sound is 100% AMAZING & super fast delivery!! #ORD-8821 😊</p>",
        height=75
    )
    if st.button("⚡ Clean Text", type="primary", key="btn_clean_sandbox"):
        try:
            from nlp_processor import clean_text
            cleaned_res = clean_text(sample_raw)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Original Raw Text:**")
                st.code(sample_raw, language="html")
            with c2:
                st.markdown("**Normalized Clean Output:**")
                st.code(cleaned_res, language="text")
        except Exception as e:
            st.error(f"Error during cleaning: {e}")

# ------------------------------------------------------------------
# Dataset Review Comparison
# ------------------------------------------------------------------
if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Text Cleaning")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)

    # Calculate metrics
    total_reviews = len(df)
    orig_lens = df['Original_Text'].astype(str).str.len()
    clean_lens = df['Cleaned_Text'].astype(str).str.len()
    avg_orig = int(orig_lens.mean()) if total_reviews > 0 else 0
    avg_clean = int(clean_lens.mean()) if total_reviews > 0 else 0
    reduction = int(((orig_lens.sum() - clean_lens.sum()) / orig_lens.sum()) * 100) if orig_lens.sum() > 0 else 0

    st.markdown("### 📊 Dataset Preprocessing Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Reviews Cleaned", f"{total_reviews:,}")
    m2.metric("Avg Raw Length", f"{avg_orig} chars")
    m3.metric("Avg Clean Length", f"{avg_clean} chars")
    m4.metric("Noise Reduced", f"{reduction}%", delta=f"-{reduction}% noise", delta_color="inverse")

    st.markdown("### 📋 Original vs Cleaned Review Comparison")
    
    # Optional search filter
    search_q = st.text_input("🔍 Search reviews by keyword:", "", placeholder="Type any word to filter...")
    display_df = df[['Original_Text', 'Cleaned_Text']].copy()
    if search_q.strip():
        display_df = display_df[
            display_df['Original_Text'].str.contains(search_q, case=False, na=False) |
            display_df['Cleaned_Text'].str.contains(search_q, case=False, na=False)
        ]
        st.caption(f"Showing {len(display_df)} matches for '{search_q}'")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Original_Text": st.column_config.TextColumn("Original Raw Review", width="large"),
            "Cleaned_Text": st.column_config.TextColumn("Normalized Cleaned Text", width="large")
        }
    )
