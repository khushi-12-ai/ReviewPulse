import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

import analyzer_service
import ui_theme

st.set_page_config(page_title="Tokenization & Stopwords | ReviewPulse", page_icon="🔤", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Tokenization & Stopwords",
    subtitle="Segments unstructured text into lexical tokens, discovers vocabulary breadth, and filters high-frequency stopwords for focused semantic analysis.",
    icon="🔤"
)

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live Tokenizer Sandbox (Test any sentence)", expanded=False):
    sandbox_input = st.text_area(
        "Enter any review or sentence to test tokenization & stopword removal:",
        value="The battery life on this wireless speaker is truly phenomenal, but the charging cable was too short!",
        height=75
    )
    if st.button("⚡ Tokenize & Filter", type="primary", key="btn_sandbox"):
        try:
            from nlp_processor import tokenize_and_process, clean_text
            cleaned_s = clean_text(sandbox_input)
            t_res = tokenize_and_process(cleaned_s)
            
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Raw Tokens", len(t_res['raw_tokens']))
            sc2.metric("Stopwords Removed", len(t_res['stopwords_removed']))
            sc3.metric("Clean Tokens Kept", len(t_res['filtered_tokens']))
            ratio = (len(t_res['stopwords_removed']) / len(t_res['raw_tokens']) * 100) if t_res['raw_tokens'] else 0
            sc4.metric("Stopword %", f"{ratio:.1f}%")
            
            st.markdown("**1. Raw Tokens (All Words):**")
            st.code(" | ".join(t_res['raw_tokens']))
            
            st.markdown("**2. Stopwords Identified & Filtered:**")
            if t_res['stopwords_removed']:
                st.markdown(" ".join([f"`{w}`" for w in t_res['stopwords_removed']]))
            else:
                st.write("None")
                
            st.markdown("**3. Remaining Cleaned Tokens:**")
            st.success(" | ".join(t_res['filtered_tokens']))
        except Exception as e:
            st.error(f"Sandbox error: {e}")

# ------------------------------------------------------------------
# Dataset-driven Tokenization Analysis
# ------------------------------------------------------------------
if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Tokenization & Stopword Filtering")
else:
    results = st.session_state['results']
    data = results['processed_data']
    df = pd.DataFrame(data)
    
    def format_tokens(toks):
        if isinstance(toks, list):
            return toks
        elif isinstance(toks, str) and toks.strip():
            return [t.strip() for t in toks.split(",") if t.strip()]
        return []

    df['Raw_Tokens_List'] = df.get('Raw_Tokens', df.get('Tokens', [])).apply(format_tokens)
    df['Stopwords_List'] = df.get('Stopwords_Removed', pd.Series([[]]*len(df))).apply(format_tokens)
    df['Clean_Tokens_List'] = df.get('Tokens', []).apply(format_tokens)
    
    total_raw_tokens = sum(df['Raw_Tokens_List'].apply(len))
    total_stopwords = sum(df['Stopwords_List'].apply(len))
    total_clean_tokens = sum(df['Clean_Tokens_List'].apply(len))
    
    all_raw_flat = [t.lower() for sub in df['Raw_Tokens_List'] for t in sub]
    unique_vocab = len(set(all_raw_flat))
    stopword_pct = (total_stopwords / total_raw_tokens * 100) if total_raw_tokens > 0 else 0
    
    st.markdown("### 📊 Dataset Tokenization Metrics")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Raw Tokens", f"{total_raw_tokens:,}")
    m2.metric("Stopwords Filtered", f"{total_stopwords:,}")
    m3.metric("Clean Tokens Kept", f"{total_clean_tokens:,}")
    m4.metric("Stopword Ratio", f"{stopword_pct:.1f}%")
    m5.metric("Unique Vocabulary", f"{unique_vocab:,}")

    tab_table, tab_charts, tab_filter = st.tabs([
        "📋 Tokenization Comparison Table",
        "📊 Stopwords & Token Distributions",
        "🔍 Search & Token Explorer"
    ])

    with tab_table:
        st.markdown("#### Review-by-Review Token Breakdown")
        st.caption("Compare raw tokens against filtered stopwords and the final retained vocabulary.")
        
        display_df = pd.DataFrame({
            "Original Review": df['Original_Text'],
            "Total Words": df['Raw_Tokens_List'].apply(len),
            "Raw Tokens": df['Raw_Tokens_List'].apply(lambda x: ", ".join(x)),
            "Stopwords Filtered": df['Stopwords_List'].apply(lambda x: ", ".join(x) if x else "(none)"),
            "Clean Tokens": df['Clean_Tokens_List'].apply(lambda x: ", ".join(x)),
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    with tab_charts:
        st.markdown("#### Top Filtered Stopwords Across Dataset")
        
        stopword_freq = results.get("stopword_frequency", [])
        if not stopword_freq and total_stopwords > 0:
            all_stops_flat = [w.lower() for sub in df['Stopwords_List'] for w in sub]
            stopword_freq = Counter(all_stops_flat).most_common(20)

        c1, c2 = st.columns(2)
        with c1:
            if stopword_freq:
                sw_df = pd.DataFrame(stopword_freq[:15], columns=["Stopword", "Occurrences"])
                fig_sw = px.bar(
                    sw_df, 
                    x='Occurrences', 
                    y='Stopword', 
                    orientation='h',
                    color='Occurrences',
                    color_continuous_scale=['#2F5FD6', '#7FA3EC', '#E7EEFC'],
                    title="Top 15 Filtered Stopwords"
                )
                fig_sw.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
                ui_theme.style_chart(fig_sw, height=400)
                st.plotly_chart(fig_sw, use_container_width=True)
            else:
                st.info("No stopword frequency data available.")

        with c2:
            st.markdown("#### Word Count Distribution")
            df['Token_Count'] = df['Raw_Tokens_List'].apply(len)
            fig_hist = px.histogram(
                df, 
                x='Token_Count', 
                nbins=15, 
                title="Review Length Histogram (Tokens per Review)",
                color_discrete_sequence=['#7FA3EC']
            )
            fig_hist.update_layout(xaxis_title="Tokens per Review", yaxis_title="Review Count")
            ui_theme.style_chart(fig_hist, height=400)
            st.plotly_chart(fig_hist, use_container_width=True)

    with tab_filter:
        st.markdown("#### Find Reviews by Specific Token")
        search_token = st.text_input("Search for token:", placeholder="e.g. battery, quality, fast, broke")
        if search_token:
            clean_search = search_token.strip().lower()
            matching_rows = df[df['Raw_Tokens_List'].apply(lambda toks: any(clean_search in str(t).lower() for t in toks))]
            st.markdown(f"Found **{len(matching_rows)}** review(s) containing token **`{clean_search}`**:")
            for idx, r in matching_rows.iterrows():
                with st.container():
                    st.markdown(f"> *\"{r['Original_Text']}\"*")
                    st.caption(f"Clean Tokens: {', '.join(r['Clean_Tokens_List'])}")
                    st.divider()
