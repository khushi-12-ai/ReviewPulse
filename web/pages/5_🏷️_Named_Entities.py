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

st.set_page_config(page_title="Named Entities | ReviewPulse", page_icon="🏷️", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Named Entity Recognition",
    subtitle="Extracts structured real-world references from review sentences — identifying brands, companies, products, geographic locations, and monetary values.",
    icon="🏷️"
)

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live Named Entity Sandbox", expanded=False):
    ner_input = st.text_area(
        "Enter text to extract entities:",
        value="I ordered the Sony WH-1000XM4 headphones from Amazon in New York for $350 and Apple customer care couldn't match the speed!",
        height=75
    )
    if st.button("⚡ Extract Entities", type="primary", key="btn_ner_sandbox"):
        try:
            from nlp_processor import extract_named_entities
            entities = extract_named_entities(ner_input)
            if entities:
                st.markdown("**Entities Found:**")
                e_cols = st.columns(min(len(entities), 4))
                for idx, e in enumerate(entities):
                    col_target = e_cols[idx % 4]
                    col_target.info(f"**{e['text']}**\n\n`{e['label']}`")
            else:
                st.info("No specific named entities recognized.")
        except Exception as e:
            st.error(f"Entity extraction error: {e}")

# ------------------------------------------------------------------
# Dataset-driven NER Analysis
# ------------------------------------------------------------------
if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Named Entity Recognition")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)
    
    # Flatten the list of entities
    all_entities = []
    for ent_list in df.get('Entities', []):
        if isinstance(ent_list, list):
            for e in ent_list:
                if isinstance(e, dict):
                    all_entities.append(e)
                elif isinstance(e, str):
                    parts = e.rsplit(" (", 1)
                    if len(parts) == 2:
                        all_entities.append({"text": parts[0], "label": parts[1].replace(")", "")})
                    
    if not all_entities:
        st.info("No named entities found in this dataset.")
    else:
        ent_df = pd.DataFrame(all_entities)
        total_ents = len(ent_df)
        unique_ents = ent_df['text'].nunique()
        top_cat = ent_df['label'].value_counts().index[0] if not ent_df.empty else "N/A"
        
        st.markdown("### 📊 Entity Statistics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Entities Extracted", f"{total_ents:,}")
        m2.metric("Unique Entity Names", f"{unique_ents:,}")
        m3.metric("Leading Entity Type", top_cat)

        ent_counts = ent_df.groupby(['text', 'label']).size().reset_index(name='count').sort_values('count', ascending=False)
        
        st.markdown("### 📋 Entity Frequency & Categories")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown("#### Top Entity Mentions")
            st.dataframe(
                ent_counts,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "text": st.column_config.TextColumn("Entity Name"),
                    "label": st.column_config.TextColumn("Category"),
                    "count": st.column_config.NumberColumn("Occurrences")
                }
            )
            
        with col2:
            st.markdown("#### Top 15 Entities Chart")
            fig = px.bar(
                ent_counts.head(15), 
                x='count', 
                y='text', 
                color='label', 
                orientation='h',
                title="Most Frequent Entities by Classification",
                color_discrete_sequence=['#7FA3EC', '#2F5FD6', '#4F8B6E', '#E4573D']
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            ui_theme.style_chart(fig, height=450)
            st.plotly_chart(fig, use_container_width=True)
