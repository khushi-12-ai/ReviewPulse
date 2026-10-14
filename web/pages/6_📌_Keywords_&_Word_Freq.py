import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

import analyzer_service
import ui_theme

st.set_page_config(page_title="Keywords & Word Frequency | ReviewPulse", page_icon="📌", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Keywords & Word Frequency",
    subtitle="Discovers the absolute most frequent terms across all reviews, alongside domain-salient key terms ranked via Term Frequency-Inverse Document Frequency (TF-IDF).",
    icon="📌"
)

if 'results' not in st.session_state:
    ui_theme.render_no_data_warning("Keywords & Word Frequency")
else:
    results = st.session_state['results']
    word_freq = results.get("word_frequency", [])
    keywords = results.get("keywords", [])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Top Frequency Word", word_freq[0][0] if word_freq else "N/A", f"{word_freq[0][1]} mentions" if word_freq else "")
    col2.metric("TF-IDF Keywords Extracted", len(keywords))
    col3.metric("Vocabulary Tracked", len(word_freq))

    st.markdown("### 📊 Frequency Distribution & Salient Terms")
    c1, c2 = st.columns([1.2, 1])
    
    with c1:
        st.markdown("#### Top 20 Most Frequent Words")
        if word_freq:
            df_wf = pd.DataFrame(word_freq[:20], columns=["Word", "Frequency"])
            fig_wf = px.bar(
                df_wf, 
                x='Frequency', 
                y='Word', 
                orientation='h',
                color='Frequency',
                color_continuous_scale=['#1E3A72', '#2F5FD6', '#7FA3EC']
            )
            fig_wf.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            ui_theme.style_chart(fig_wf, height=450)
            st.plotly_chart(fig_wf, use_container_width=True)
        else:
            st.info("No word frequency data available.")
            
    with c2:
        st.markdown("#### Salient TF-IDF Keywords")
        st.caption("Words mathematically determined to be characteristic of this specific customer review dataset:")
        if keywords:
            kw_html = "".join([f'<span style="display:inline-block; background:rgba(127,163,236,0.18); border:1px solid rgba(127,163,236,0.35); border-radius:999px; padding:4px 14px; margin:4px; font-weight:600; font-size:0.88rem; color:#ffffff;">✨ {kw}</span>' for kw in keywords])
            st.markdown(f'<div style="line-height:2.2; margin-bottom:16px;">{kw_html}</div>', unsafe_allow_html=True)
            
            st.markdown("#### Word Frequency Table")
            if word_freq:
                st.dataframe(
                    pd.DataFrame(word_freq, columns=["Word", "Count"]),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No keywords extracted.")
