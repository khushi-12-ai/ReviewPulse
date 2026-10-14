import streamlit as st
import pandas as pd
import sys
import os

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

import analyzer_service
import ui_theme

st.set_page_config(page_title="Regex Extraction | ReviewPulse", page_icon="🔍", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Regex Pattern Extraction",
    subtitle="Detects and extracts structured metadata and sensitive customer identifiers — including Emails, Phone Numbers, and Order IDs — using deterministic regular expressions.",
    icon="🔍"
)

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live Regex Pattern Extractor", expanded=False):
    regex_test = st.text_input(
        "Enter text containing contact info or order references:",
        value="Please update me at support@customer.com or call +1-800-555-0199 regarding order #ORD-99281."
    )
    if st.button("⚡ Extract Patterns", type="primary", key="btn_regex_test"):
        try:
            from nlp_processor import extract_regex_patterns
            pats = extract_regex_patterns(regex_test)
            r1, r2, r3 = st.columns(3)
            r1.metric("Emails Found", ", ".join(pats['emails']) if pats['emails'] else "None")
            r2.metric("Phones Found", ", ".join(pats['phones']) if pats['phones'] else "None")
            r3.metric("Order IDs Found", ", ".join(pats['order_ids']) if pats['order_ids'] else "None")
        except Exception as e:
            st.error(f"Error: {e}")

# ------------------------------------------------------------------
# Dataset Regex Extraction
# ------------------------------------------------------------------
if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Regex Pattern Extraction")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)
    
    def join_list(lst):
        if isinstance(lst, list) and lst:
            return ", ".join(str(i) for i in lst)
        return ""
        
    df['Emails_Str'] = df.get('Emails', pd.Series(dtype=object)).apply(join_list)
    df['Phones_Str'] = df.get('Phones', pd.Series(dtype=object)).apply(join_list)
    df['Orders_Str'] = df.get('Order_IDs', pd.Series(dtype=object)).apply(join_list)
    
    total_emails = (df['Emails_Str'] != "").sum()
    total_phones = (df['Phones_Str'] != "").sum()
    total_orders = (df['Orders_Str'] != "").sum()

    st.markdown("### 📊 Extracted Identifiers Summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Reviews with Emails", f"{total_emails:,}")
    m2.metric("Reviews with Phone Numbers", f"{total_phones:,}")
    m3.metric("Reviews with Order IDs", f"{total_orders:,}")

    has_extraction = (df['Emails_Str'] != "") | (df['Phones_Str'] != "") | (df['Orders_Str'] != "")
    display_df = df[has_extraction]
    
    st.markdown("### 📋 Extracted Structured Records")
    if display_df.empty:
        st.info("No emails, phone numbers, or order IDs were detected in the active reviews dataset.")
    else:
        st.dataframe(
            display_df[['Original_Text', 'Emails_Str', 'Phones_Str', 'Orders_Str']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Original_Text": st.column_config.TextColumn("Customer Review", width="large"),
                "Emails_Str": st.column_config.TextColumn("Email Addresses", width="medium"),
                "Phones_Str": st.column_config.TextColumn("Phone Numbers", width="medium"),
                "Orders_Str": st.column_config.TextColumn("Order Numbers", width="medium"),
            }
        )
