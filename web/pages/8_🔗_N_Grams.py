import streamlit as st
import pandas as pd
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

import analyzer_service
import ui_theme

st.set_page_config(page_title="N-Grams Analysis | ReviewPulse", page_icon="🔗", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="N-Gram Phrase Analysis",
    subtitle="Extracts contiguous multi-word sequences (2-word Bigrams and 3-word Trigrams) to capture meaningful customer sentiment contexts that isolated words obscure.",
    icon="🔗"
)

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live N-Gram Sandbox (Test any text)", expanded=False):
    ngram_test = st.text_input(
        "Enter a review to extract multi-word combinations:",
        value="The battery life is incredible and customer support was lightning fast!"
    )
    if st.button("⚡ Extract Phrases", type="primary", key="btn_ngram_test"):
        try:
            from nlp_processor import extract_ngrams, clean_text
            cleaned_ng = clean_text(ngram_test)
            phrases = extract_ngrams(cleaned_ng, n_range=(2, 3), top_n=5)
            if phrases:
                st.markdown("**Key Multi-Word Phrases:**")
                st.write(" • ".join([f"`{p}`" for p in phrases]))
            else:
                st.info("No repeated multi-word patterns found.")
        except Exception as e:
            st.error(f"Error: {e}")

# ------------------------------------------------------------------
# Dataset N-Grams
# ------------------------------------------------------------------
if 'results' not in st.session_state:
    ui_theme.render_no_data_warning("N-Gram Phrase Analysis")
else:
    results = st.session_state['results']
    ngrams = results.get("ngrams", [])
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 🧩 Top Multi-Word Phrases")
        if ngrams:
            st.caption("Salient 2-word and 3-word combinations identified using TF-IDF N-gram analysis:")
            ngram_badges = "".join([f'<span style="display:inline-block; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); border-radius:999px; padding:6px 16px; margin:4px; font-weight:600; font-size:0.9rem; color:#ffffff;">🔗 {p}</span>' for p in ngrams])
            st.markdown(f'<div style="line-height:2.4; margin-bottom:20px;">{ngram_badges}</div>', unsafe_allow_html=True)
            
            df_ngrams = pd.DataFrame(ngrams, columns=["Extracted Key Phrase"])
            df_ngrams['Phrase Type'] = df_ngrams['Extracted Key Phrase'].apply(lambda x: f"{len(x.split())}-Gram")
            st.dataframe(df_ngrams, use_container_width=True, hide_index=True)
        else:
            st.info("No N-grams extracted from this dataset.")
            
    with col2:
        st.markdown("### 💡 Why N-Grams Matter")
        st.markdown("""
        Single words alone often miss crucial sentiment nuance:
        - *"Not good"* contains the positive word *"good"*, but the bigram reveals **negative feedback**.
        - *"Battery life"* or *"customer service"* group attributes together rather than analyzing *"battery"* and *"life"* separately.
        - Trigrams like *"value for money"* capture entire customer value propositions.
        """)
