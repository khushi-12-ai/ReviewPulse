import streamlit as st
import pandas as pd
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

BACKEND_DIR = os.path.abspath(os.path.join(WEB_DIR, "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from report_generator import generate_pdf_report, generate_excel_report
import analyzer_service
import ui_theme

st.set_page_config(page_title="Export Reports | ReviewPulse", page_icon="📄", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Export Reports & Data",
    subtitle="Generate publication-grade PDF executive briefings with charts & AI summaries, or download full-fidelity enriched Excel spreadsheets with all NLP features.",
    icon="📄"
)

if 'results' not in st.session_state:
    ui_theme.render_no_data_warning("Export Reports")
else:
    results = st.session_state['results']
    processed_records = results.get('processed_data', [])
    processed_df = pd.DataFrame(processed_records)
    total_revs = len(processed_df)
    
    st.markdown("### 📊 Export Dataset Summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Reviews Available", f"{total_revs:,}")
    m2.metric("Enriched NLP Attributes", len(processed_df.columns))
    m3.metric("Export Formats", "PDF + Excel (.xlsx)")

    st.markdown("### 📥 Instant Downloads")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Executive PDF Intelligence Brief")
        st.caption("C-level executive briefing featuring sentiment distribution, top customer complaints & praise, key entity mentions, and AI insights.")
        try:
            pdf_buffer = generate_pdf_report(results)
            st.download_button(
                label="📥 Download Executive PDF Report",
                data=pdf_buffer.getvalue(),
                file_name="reviewpulse_executive_report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Could not generate PDF: {e}")
            
    with col2:
        st.markdown("#### 📊 Full Excel Master Dataset")
        st.caption("Complete tabular export including Cleaned Text, Tokens, Stems, Lemmas, POS Tags, Sentiment Polarity, and Authenticity Flags.")
        try:
            export_df = processed_df.copy()
            for col in export_df.columns:
                export_df[col] = export_df[col].apply(lambda x: ", ".join(str(i) for i in x) if isinstance(x, (list, tuple)) else x)
                
            excel_buffer = generate_excel_report(export_df)
            st.download_button(
                label="📥 Download Full Excel Master (.xlsx)",
                data=excel_buffer.getvalue(),
                file_name="reviewpulse_master_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="secondary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Could not generate Excel: {e}")
            
    st.divider()
    st.markdown("### 🔍 Master Dataset Preview")
    st.dataframe(processed_df.head(10), use_container_width=True)
