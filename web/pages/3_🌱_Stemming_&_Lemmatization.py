import streamlit as st
import pandas as pd
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

import analyzer_service
import ui_theme

st.set_page_config(page_title="Stemming & Lemmatization | ReviewPulse", page_icon="🌱", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Stemming & Lemmatization",
    subtitle="Reduces inflectional forms of words to their base roots — contrasting fast rule-based suffix chopping (Porter Stemmer) against vocabulary-aware morphological lemmatization (spaCy/WordNet).",
    icon="🌱"
)

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live Stemming vs Lemmatization Sandbox", expanded=False):
    test_phrase = st.text_input(
        "Enter words or a sentence to compare roots in real-time:",
        value="The delivered packages are arriving faster and better than expected"
    )
    if st.button("⚡ Compare Roots", type="primary", key="btn_stem_lemma_test"):
        try:
            from nlp_processor import tokenize_and_process, clean_text
            cleaned = clean_text(test_phrase)
            res = tokenize_and_process(cleaned)
            
            comp_data = []
            for w, s, l in zip(res['filtered_tokens'], res['stems'], res['lemmas']):
                diff = "⚡ Divergent" if s.lower() != l.lower() else "✅ Identical"
                comp_data.append({"Original Token": w, "Porter Stem (Chopped)": s, "Lemma (Dictionary Root)": l, "Status": diff})
                
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error during root comparison: {e}")

# ------------------------------------------------------------------
# Dataset-driven Stemming & Lemmatization
# ------------------------------------------------------------------
if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Stemming & Lemmatization")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)

    def to_list(val):
        if isinstance(val, list):
            return val
        elif isinstance(val, str) and val.strip():
            return [v.strip() for v in val.split(",") if v.strip()]
        return []

    df['Tokens_Clean'] = df.get('Tokens', []).apply(to_list)
    df['Stems_Clean'] = df.get('Stems', []).apply(to_list)
    df['Lemmas_Clean'] = df.get('Lemmas', []).apply(to_list)

    # Compute word-level pairs
    seen_words = set()
    pairs = []
    for _, row in df.iterrows():
        toks = row['Tokens_Clean']
        stms = row['Stems_Clean']
        lms = row['Lemmas_Clean']
        for w, s, l in zip(toks, stms, lms):
            w_low = w.lower()
            if w_low not in seen_words:
                seen_words.add(w_low)
                diff = "⚡ Divergent" if s.lower() != l.lower() else "✅ Identical"
                pairs.append({
                    "Original Word": w,
                    "Porter Stem": s,
                    "Dictionary Lemma": l,
                    "Difference": diff
                })

    pairs_df = pd.DataFrame(pairs)
    total_unique_words = len(pairs_df)
    divergent_count = len(pairs_df[pairs_df['Difference'] == "⚡ Divergent"]) if total_unique_words > 0 else 0
    divergence_rate = (divergent_count / total_unique_words * 100) if total_unique_words > 0 else 0

    st.markdown("### 📊 Morphological Statistics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Unique Vocabulary Words", f"{total_unique_words:,}")
    m2.metric("Stem vs Lemma Matches", f"{total_unique_words - divergent_count:,}")
    m3.metric("Divergent Roots", f"{divergent_count:,}")
    m4.metric("Divergence Rate", f"{divergence_rate:.1f}%", help="Percentage of words where the heuristic stemmer differs from the morphological lemmatizer")

    st.markdown("### 📋 Root Reduction Comparison")
    view_option = st.radio("Display Format", ["Word-Level Root Pairs (Detailed)", "Review-Level Text Table"], horizontal=True)

    if view_option == "Word-Level Root Pairs (Detailed)":
        if not pairs_df.empty:
            c_f1, c_f2 = st.columns([1, 2])
            with c_f1:
                diff_only = st.checkbox("Show only words where Stem and Lemma diverge", value=False)
            with c_f2:
                filter_text = st.text_input("Filter by word:", "", placeholder="e.g. deliver, batter, qual")
            
            filtered_df = pairs_df.copy()
            if diff_only:
                filtered_df = filtered_df[filtered_df['Difference'] == "⚡ Divergent"]
            if filter_text.strip():
                filtered_df = filtered_df[filtered_df['Original Word'].str.contains(filter_text, case=False, na=False)]
                
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            st.caption(f"Displaying {len(filtered_df)} root mappings.")
        else:
            st.info("No tokens found to compare.")
    else:
        review_df = pd.DataFrame({
            "Original Review": df['Original_Text'],
            "Filtered Tokens": df['Tokens_Clean'].apply(lambda x: ", ".join(x)),
            "Porter Stems": df['Stems_Clean'].apply(lambda x: ", ".join(x)),
            "Lemmas (Base Words)": df['Lemmas_Clean'].apply(lambda x: ", ".join(x))
        })
        st.dataframe(review_df, use_container_width=True, hide_index=True)
