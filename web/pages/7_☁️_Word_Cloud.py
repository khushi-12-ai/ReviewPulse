import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

import analyzer_service
import ui_theme

st.set_page_config(page_title="Word Cloud | ReviewPulse", page_icon="☁️", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Word Cloud Visualization",
    subtitle="Aesthetic high-impact visual representation of the most recurring themes, topics, and customer sentiments across all reviews.",
    icon="☁️"
)

if 'results' not in st.session_state:
    ui_theme.render_no_data_warning("Word Cloud")
else:
    results = st.session_state['results']
    word_freq = results.get("word_frequency", [])
    
    if word_freq:
        freq_dict = {word: count for word, count in word_freq if len(word) > 1}
        
        st.markdown("### ⚙️ Visualization Settings")
        c1, c2, c3 = st.columns(3)
        with c1:
            bg_choice = st.selectbox("Background Theme", ["Midnight Dark (#14203E)", "Clean White Paper"], index=0)
            bg_color = "#14203E" if "Midnight" in bg_choice else "#FFFFFF"
        with c2:
            colormap = st.selectbox("Color Palette", ["plasma", "viridis", "cool", "Blues_r", "magma", "ocean"], index=0)
        with c3:
            max_words = st.slider("Max Word Limit", min_value=15, max_value=120, value=60, step=5)

        with st.spinner("Generating aesthetic word cloud..."):
            wc = WordCloud(
                width=1000, 
                height=500, 
                background_color=bg_color,
                colormap=colormap,
                max_words=max_words,
                prefer_horizontal=0.85,
                margin=8
            ).generate_from_frequencies(freq_dict)
            
            fig_wc, ax = plt.subplots(figsize=(12, 6), facecolor=bg_color)
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(fig_wc)

        st.caption(f"Showing the top {min(len(freq_dict), max_words)} keywords weighted by occurrence frequency.")
    else:
        st.info("No word frequency data available to generate a word cloud.")
