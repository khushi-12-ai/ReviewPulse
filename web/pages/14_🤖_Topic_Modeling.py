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

st.set_page_config(page_title="Topic Modeling | ReviewPulse", page_icon="🤖", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Unsupervised Topic Modeling",
    subtitle="Clusters customer reviews into thematic concepts and latent clusters using Latent Dirichlet Allocation (LDA) natural language processing.",
    icon="🤖"
)

if 'results' not in st.session_state:
    ui_theme.render_no_data_warning("Topic Modeling")
else:
    topics = st.session_state['results'].get('topics', [])
    
    if not topics:
        st.info("No topics were generated. Ensure your dataset has sufficient text variety and sample volume (at least 5+ detailed reviews) for LDA modeling.")
    else:
        st.markdown(f"### 🎯 Discovered {len(topics)} Latent Topics")
        
        cols = st.columns(len(topics))
        for idx, topic in enumerate(topics):
            with cols[idx]:
                st.metric(f"Topic {topic['Topic_ID']}", topic['Name'], f"{topic['Count']} reviews")

        st.divider()

        for topic in topics:
            c1, c2 = st.columns([1, 1.2])
            with c1:
                st.markdown(f"#### Topic {topic['Topic_ID']}: {topic['Name']}")
                st.caption(f"Cluster representation: **{topic['Count']} customer reviews**")
                word_badges = "".join([f'<span style="display:inline-block; background:rgba(47,95,214,0.2); border:1px solid rgba(127,163,236,0.4); border-radius:999px; padding:4px 12px; margin:4px; font-weight:600; font-size:0.85rem; color:#ffffff;">🏷️ {w}</span>' for w in topic['Top_Words']])
                st.markdown(f'<div style="line-height:2.2; margin-top:12px;">{word_badges}</div>', unsafe_allow_html=True)
                
            with c2:
                words = topic['Top_Words']
                df_words = pd.DataFrame({"Word": words, "Relevance Score": range(len(words), 0, -1)})
                fig = px.bar(
                    df_words, 
                    x='Relevance Score', 
                    y='Word', 
                    orientation='h', 
                    title=f"Key Discriminative Terms (Topic {topic['Topic_ID']})",
                    color='Relevance Score',
                    color_continuous_scale=['#1E3A72', '#2F5FD6', '#7FA3EC']
                )
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                ui_theme.style_chart(fig, height=280)
                st.plotly_chart(fig, use_container_width=True)
            st.divider()
