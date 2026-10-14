import streamlit as st
import pandas as pd
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

import analyzer_service
import ui_theme

st.set_page_config(page_title="POS Tagging | ReviewPulse", page_icon="🏷️", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Part-of-Speech (POS) Tagging",
    subtitle="Categorizes every token in the customer review into syntactic grammatical categories (Nouns, Verbs, Adjectives, Adverbs) to understand syntactic patterns.",
    icon="🏷️"
)

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live POS Tagging Sandbox", expanded=False):
    pos_input = st.text_input(
        "Enter any sentence to inspect parts of speech:",
        value="The sleek modern smartwatch syncs quickly with my phone."
    )
    if st.button("⚡ Tag Words", type="primary", key="btn_pos_test"):
        try:
            from nlp_processor import pos_tag_text
            tags = pos_tag_text(pos_input)
            if tags:
                tag_cols = st.columns(min(len(tags), 6))
                for idx, (word, tag) in enumerate(tags):
                    col = tag_cols[idx % 6]
                    col.info(f"**{word}**\n\n`{tag}`")
        except Exception as e:
            st.error(f"Error: {e}")

# ------------------------------------------------------------------
# Dataset POS Tagging
# ------------------------------------------------------------------
if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("POS Tagging")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)
    
    st.markdown("### 📋 POS Tags per Customer Review")
    
    def format_pos(pos_list):
        if not isinstance(pos_list, list):
            return ""
        return " | ".join([f"{word} [{tag}]" for word, tag in pos_list])
        
    df['POS_Formatted'] = df.get('POS_Tags', pd.Series(dtype=object)).apply(format_pos)
    
    st.dataframe(
        df[['Original_Text', 'POS_Formatted']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Original_Text": st.column_config.TextColumn("Customer Review", width="medium"),
            "POS_Formatted": st.column_config.TextColumn("Grammatical POS Tags (Word [Tag])", width="large")
        }
    )
