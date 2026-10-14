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

st.set_page_config(page_title="Dashboard Overview | ReviewPulse", layout="wide", page_icon="📊")
ui_theme.apply_theme()

# ------------------------------------------------------------------
# CASE 1: NO DATASET LOADED YET
# ------------------------------------------------------------------
if 'results' not in st.session_state:
    ui_theme.render_page_header(
        title="Dashboard Overview", 
        subtitle="Upload a customer review spreadsheet or load sample reviews to unlock executive sentiment and AI intelligence.",
        icon="📊"
    )
    
    col_up, col_sample = st.columns([1.6, 1])
    
    with col_up:
        st.markdown("### 📁 Upload Review File")
        dash_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls", "tsv"], key="dash_uploader")
        
        if dash_file is not None:
            try:
                f_bytes = dash_file.getvalue()
                p_df = analyzer_service.read_file_into_df(f_bytes, dash_file.name)
                det_text, det_date = analyzer_service.detect_columns(p_df)
                p_cols = list(p_df.columns)
                
                c1, c2 = st.columns(2)
                with c1:
                    t_idx = p_cols.index(det_text) if det_text in p_cols else 0
                    chosen_text = st.selectbox("Text Column (Required)", options=p_cols, index=t_idx, key="dash_text_col")
                with c2:
                    d_options = ["None"] + p_cols
                    d_idx = d_options.index(det_date) if det_date in d_options else 0
                    chosen_date_raw = st.selectbox("Date Column (Optional)", options=d_options, index=d_idx, key="dash_date_col")
                    chosen_date = None if chosen_date_raw == "None" else chosen_date_raw
                
                if st.button("✨ Analyze Reviews", type="primary", use_container_width=True, key="dash_btn_analyze"):
                    with st.spinner("Processing reviews with NLP engine... ☕"):
                        res = analyzer_service.run_analysis(f_bytes, dash_file.name, chosen_text, chosen_date)
                        st.session_state['results'] = res
                        st.session_state['dataset_name'] = dash_file.name
                        st.success("Analysis complete! Rendering dashboard...")
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

    with col_sample:
        st.markdown("### ⚡ Quick Start")
        st.markdown("Want to explore all NLP features right away? Click below to instantly load a rich, multi-category customer review dataset.")
        if st.button("🚀 Load Sample Dataset", type="secondary", use_container_width=True, key="dash_load_sample"):
            with st.spinner("Loading sample reviews... ☕"):
                try:
                    s_df = analyzer_service.get_sample_dataset()
                    res = analyzer_service.run_analysis_local(s_df, "Review_Text", "Date")
                    st.session_state['results'] = res
                    st.session_state['dataset_name'] = "Sample E-Commerce Reviews"
                    st.success("Loaded! Rendering dashboard...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load sample dataset: {e}")

    st.stop()

# ------------------------------------------------------------------
# CASE 2: DATASET LOADED -> RENDER DASHBOARD
# ------------------------------------------------------------------
ui_theme.render_page_header(
    title="Executive Overview", 
    subtitle="High-level customer sentiment distribution, CSAT scores, AI summaries, and deep NLP intelligence.",
    icon="📊"
)

# Top Action Toolbar
col_info, col_reset = st.columns([4, 1.3])
with col_reset:
    if st.button("🔄 Upload New File", use_container_width=True):
        del st.session_state['results']
        if 'dataset_name' in st.session_state:
            del st.session_state['dataset_name']
        st.rerun()

# Expandable file switcher on Dashboard
with st.expander("📤 Switch Dataset or Upload Another File", expanded=False):
    sw_file = st.file_uploader("Upload replacement file", type=["csv", "xlsx", "xls", "tsv"], key="sw_uploader")
    if sw_file is not None:
        try:
            sw_bytes = sw_file.getvalue()
            sw_df = analyzer_service.read_file_into_df(sw_bytes, sw_file.name)
            sw_text, sw_date = analyzer_service.detect_columns(sw_df)
            sw_cols = list(sw_df.columns)
            
            sc1, sc2 = st.columns(2)
            with sc1:
                sw_chosen_text = st.selectbox("Text Column", options=sw_cols, index=sw_cols.index(sw_text) if sw_text in sw_cols else 0, key="sw_t")
            with sc2:
                sw_d_opts = ["None"] + sw_cols
                sw_chosen_date = st.selectbox("Date Column", options=sw_d_opts, index=sw_d_opts.index(sw_date) if sw_date in sw_d_opts else 0, key="sw_d")
                sw_final_date = None if sw_chosen_date == "None" else sw_chosen_date
                
            if st.button("✨ Process New File", type="primary", key="sw_btn"):
                with st.spinner("Analyzing..."):
                    res = analyzer_service.run_analysis(sw_bytes, sw_file.name, sw_chosen_text, sw_final_date)
                    st.session_state['results'] = res
                    st.session_state['dataset_name'] = sw_file.name
                    st.success("New file loaded!")
                    st.rerun()
        except Exception as e:
            st.error(f"Error processing file: {e}")

results = st.session_state['results']

# KPIs and AI Summary in columns
col_kpis, col_ai = st.columns([2.1, 1])

with col_kpis:
    sentiment = results.get("sentiment_distribution", {})
    total_reviews = sum(sentiment.values()) if sentiment else 0
    pos = sentiment.get("Positive", 0)
    neu = sentiment.get("Neutral", 0)
    neg = sentiment.get("Negative", 0)
    
    processed_df = pd.DataFrame(results.get("processed_data", []))
    spam_count = processed_df['Is_Spam'].sum() if 'Is_Spam' in processed_df.columns else 0
    
    if total_reviews > 0:
        pos_pct = pos / total_reviews
        neu_pct = neu / total_reviews
        spam_pct = spam_count / total_reviews
        csat = (pos_pct * 100) + (neu_pct * 50) - (spam_pct * 20)
        csat = max(0, min(100, csat))
    else:
        csat = 0
        
    m0, m1, m2, m3, m4 = st.columns(5)
    m0.metric("🏆 CSAT Score", f"{csat:.1f}/100")
    m1.metric("Total Reviews", total_reviews)
    m2.metric("😊 Positive", pos)
    m3.metric("😐 Neutral", neu)
    m4.metric("😡 Negative", neg)

with col_ai:
    with st.expander("🤖 Click to View AI Insights", expanded=True):
        st.markdown(results.get("ai_summary", "No summary available."))

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🔍 Deep-Dive NLP Features")
st.caption("Select an intelligence card below to explore full linguistic breakdowns, tokenization, or export reports.")

tab1, tab2, tab3, tab4 = st.tabs([
    "🧹 Text Preprocessing", 
    "📊 Feature Extraction", 
    "🧠 NLP & Intelligence", 
    "📈 Reports & Analytics"
])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ui_theme.render_feature_card("🧹", "Text Cleaning", "Remove HTML tags, special chars, URLs, and standardizes case.")
        if st.button("Explore Cleaning", key="nav_clean", use_container_width=True):
            st.switch_page("pages/1_🧹_Text_Cleaning.py")
    with col2:
        ui_theme.render_feature_card("🔤", "Tokenization", "Split text into words and filter out common stopwords.")
        if st.button("Explore Tokens", key="nav_tokens", use_container_width=True):
            st.switch_page("pages/2_🔤_Tokenization_&_Stopwords.py")
    with col3:
        ui_theme.render_feature_card("🌱", "Stemming & Lemma", "Reduce words to their root forms (e.g. running -> run).")
        if st.button("Explore Roots", key="nav_stem_lemma", use_container_width=True):
            st.switch_page("pages/3_🌱_Stemming_&_Lemmatization.py")
    with col4:
        ui_theme.render_feature_card("🏷️", "POS Tagging", "Tag words with grammatical roles like nouns, verbs, etc.")
        if st.button("Explore POS", key="nav_pos", use_container_width=True):
            st.switch_page("pages/9_🏷️_POS_Tagging.py")

with tab2:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ui_theme.render_feature_card("📌", "Keywords & Freq", "Find high-impact terms and frequency counts in reviews.")
        if st.button("Explore Freq", key="nav_freq", use_container_width=True):
            st.switch_page("pages/6_📌_Keywords_&_Word_Freq.py")
    with col2:
        ui_theme.render_feature_card("☁️", "Word Cloud", "Generate beautiful word clouds of prominent review phrases.")
        if st.button("Explore Cloud", key="nav_cloud", use_container_width=True):
            st.switch_page("pages/7_☁️_Word_Cloud.py")
    with col3:
        ui_theme.render_feature_card("🔗", "N-Grams", "Analyze contiguous sequences of words (bigrams, trigrams).")
        if st.button("Explore N-Grams", key="nav_ngrams", use_container_width=True):
            st.switch_page("pages/8_🔗_N_Grams.py")
    with col4:
        ui_theme.render_feature_card("🔍", "Regex Extraction", "Automatically pull Order IDs, emails, and phone numbers.")
        if st.button("Explore Regex", key="nav_regex", use_container_width=True):
            st.switch_page("pages/10_🔍_Regex_Extraction.py")

with tab3:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        ui_theme.render_feature_card("😊", "Sentiment Analysis", "Compute sentiment polarity and positive/negative/neutral breakdown.")
        if st.button("Explore Sentiment", key="nav_sentiment", use_container_width=True):
            st.switch_page("pages/4_😊_Sentiment_Analysis.py")
    with col2:
        ui_theme.render_feature_card("🏷️", "Named Entities", "Detect locations, organizations, dates, and names using NER.")
        if st.button("Explore Entities", key="nav_ner", use_container_width=True):
            st.switch_page("pages/5_🏷️_Named_Entities.py")
    with col3:
        ui_theme.render_feature_card("🧪", "Spam Detection", "Flag potential fake reviews, duplicates, or spam patterns.")
        if st.button("Explore Spam", key="nav_spam", use_container_width=True):
            st.switch_page("pages/13_🧪_Spam_Detection.py")
    with col4:
        ui_theme.render_feature_card("🤖", "Topic Modeling", "Group reviews dynamically into distinct categories using LDA.")
        if st.button("Explore Topics", key="nav_topics", use_container_width=True):
            st.switch_page("pages/14_🤖_Topic_Modeling.py")
    with col5:
        ui_theme.render_feature_card("📈", "Sentiment Trends", "Track how user opinions change over dates and time periods.")
        if st.button("Explore Trends", key="nav_trends", use_container_width=True):
            st.switch_page("pages/15_📈_Sentiment_Trends.py")

with tab4:
    col1, col2, col3 = st.columns(3)
    with col1:
        ui_theme.render_feature_card("🌍", "Multilingual", "Auto-translate and evaluate non-English customer reviews.")
        if st.button("Explore Languages", key="nav_multilingual", use_container_width=True):
            st.switch_page("pages/12_🌍_Multilingual_Analysis.py")
    with col2:
        ui_theme.render_feature_card("📄", "Export Reports", "Download professional PDF summaries or Excel datasets.")
        if st.button("Explore Reports", key="nav_reports", use_container_width=True):
            st.switch_page("pages/11_📄_Export_Reports.py")
