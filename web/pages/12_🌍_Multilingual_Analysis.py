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

st.set_page_config(page_title="Multilingual Analysis | ReviewPulse", page_icon="🌍", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Multilingual Review Analysis",
    subtitle="Automatically identifies customer review languages and provides dynamic neural machine translation to English for global customer intelligence.",
    icon="🌍"
)

LANG_MAP = {
    'en': 'English 🇺🇸',
    'es': 'Spanish 🇪🇸',
    'fr': 'French 🇫🇷',
    'de': 'German 🇩🇪',
    'it': 'Italian 🇮🇹',
    'pt': 'Portuguese 🇵🇹',
    'zh-cn': 'Chinese 🇨🇳',
    'zh-tw': 'Chinese 🇨🇳',
    'ja': 'Japanese 🇯🇵',
    'ko': 'Korean 🇰🇷',
    'ru': 'Russian 🇷🇺',
    'ar': 'Arabic 🇸🇦',
    'hi': 'Hindi 🇮🇳',
    'nl': 'Dutch 🇳🇱',
    'tr': 'Turkish 🇹🇷',
    'vi': 'Vietnamese 🇻🇳',
    'pl': 'Polish 🇵🇱',
    'sv': 'Swedish 🇸🇪',
    'no': 'Norwegian 🇳🇴',
    'fi': 'Finnish 🇫🇮',
    'da': 'Danish 🇩🇰',
    'unknown': 'Unknown ❓'
}

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live Language Detector & Translator", expanded=False):
    multi_input = st.text_input(
        "Enter non-English review text to detect and translate:",
        value="¡Este producto es absolutamente fantástico! La calidad supera todas mis expectativas."
    )
    if st.button("⚡ Detect & Translate", type="primary", key="btn_multi_test"):
        try:
            with st.spinner("Detecting language and translating... 🌐"):
                from multilingual import detect_and_translate
                trans_text, lang_code = detect_and_translate(multi_input)
                lang_label = LANG_MAP.get(lang_code, lang_code.upper())
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.info(f"**Detected Language:** {lang_label}")
            with m_col2:
                st.success(f"**English Translation:**\n\n\"{trans_text}\"")
        except Exception as e:
            st.error(f"Translation error: {e}")

# ------------------------------------------------------------------
# Dataset-driven Multilingual Analysis
# ------------------------------------------------------------------
if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Multilingual Analysis")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)
    
    if 'Original_Language' in df.columns:
        df['Language_Name'] = df['Original_Language'].apply(lambda x: LANG_MAP.get(str(x).lower(), f"{str(x).upper()} 🌍"))
        
        total_reviews = len(df)
        non_english_df = df[~df['Original_Language'].isin(['en', 'unknown'])]
        non_english_count = len(non_english_df)
        english_count = len(df[df['Original_Language'] == 'en'])
        unknown_count = len(df[df['Original_Language'] == 'unknown'])
        total_languages = df['Original_Language'].nunique()
        non_english_pct = (non_english_count / total_reviews) * 100 if total_reviews > 0 else 0
        
        st.markdown("### 📊 Global Language KPIs")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌍 Total Languages", total_languages)
        col2.metric("🇺🇸 English Reviews", english_count)
        col3.metric("📝 Non-English Reviews", non_english_count)
        col4.metric("📊 % Non-English", f"{non_english_pct:.1f}%")
        
        st.markdown("### 📈 Language Distribution & Translation Pipeline")
        col_chart, col_info = st.columns([1.2, 1])
        
        with col_chart:
            lang_counts = df['Language_Name'].value_counts().reset_index()
            lang_counts.columns = ['Language', 'Count']
            
            fig = px.pie(
                lang_counts, 
                values='Count', 
                names='Language', 
                hole=0.45,
                color_discrete_sequence=['#2F5FD6', '#7FA3EC', '#4F8B6E', '#E4573D', '#F59E0B']
            )
            ui_theme.style_chart(fig, height=350)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_info:
            st.markdown("#### ⚡ NLP Architecture Note")
            st.info(
                """
                - **Language Detection**: Reviews are analyzed using fast, reliable language identification.
                - **Dynamic Translation**: Non-English feedback is translated directly to English.
                - **Downstream Accuracy**: Downstream tasks (VADER Sentiment, POS, Topic Modeling) operate on normalized translations for optimal statistical power.
                """
            )
            
        st.markdown("### 🕵️ Review Explorer by Language")
        unique_langs = sorted(df['Language_Name'].unique())
        selected_lang = st.selectbox("Filter Reviews by Language:", options=["All Languages"] + unique_langs)
        
        filtered_df = df if selected_lang == "All Languages" else df[df['Language_Name'] == selected_lang]
        
        display_df = filtered_df.copy()
        cols_to_show = {
            'Language_Name': 'Language',
            'Original_Text': 'Original Text',
            'Translated_Text': 'English Translation',
            'Sentiment_Label': 'Sentiment'
        }
        existing_cols = [c for c in cols_to_show.keys() if c in display_df.columns]
        final_df = display_df[existing_cols].rename(columns={c: cols_to_show[c] for c in existing_cols})
        
        st.dataframe(final_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Multilingual data is not available. Ensure you are running the latest backend.")
