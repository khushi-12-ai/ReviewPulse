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

st.set_page_config(page_title="Spam Detection | ReviewPulse", page_icon="🧪", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Spam & Authenticity Detection",
    subtitle="Detects suspicious reviews, automated bot submissions, duplicate spam, and low-effort feedback to ensure actionable customer insights.",
    icon="🧪"
)

if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Spam & Authenticity Detection")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)
    
    if 'Is_Spam' in df.columns:
        spam_counts = df['Is_Spam'].value_counts()
        total_reviews = len(df)
        
        spam_count = int(spam_counts.get(True, 0))
        genuine_count = int(spam_counts.get(False, 0))
        genuine_pct = (genuine_count / total_reviews * 100) if total_reviews > 0 else 0
        spam_pct = (spam_count / total_reviews * 100) if total_reviews > 0 else 0
        
        st.markdown("### 📊 Feedback Authenticity KPIs")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Reviews Analyzed", f"{total_reviews:,}")
        m2.metric("Authentic Reviews", f"{genuine_pct:.1f}%", f"{genuine_count} verified")
        m3.metric("Suspicious / Spam", f"{spam_pct:.1f}%", f"-{spam_count} flagged", delta_color="inverse")
        m4.metric("Dataset Integrity", "Healthy ✅" if spam_pct < 15 else "Attention Required ⚠️")

        st.markdown("### 📈 Authenticity & Reasons Breakdown")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Spam Classification Proportions")
            auth_df = pd.DataFrame({
                "Status": ["Genuine", "Suspicious / Spam"],
                "Count": [genuine_count, spam_count]
            })
            fig_auth = px.pie(
                auth_df, 
                values='Count', 
                names='Status', 
                hole=0.45,
                color='Status',
                color_discrete_map={"Genuine": "#4F8B6E", "Suspicious / Spam": "#E4573D"}
            )
            ui_theme.style_chart(fig_auth, height=350)
            st.plotly_chart(fig_auth, use_container_width=True)
            
        with col2:
            st.markdown("#### Primary Detection Triggers")
            reason_counts = df[df['Is_Spam'] == True]['Spam_Reason'].value_counts().reset_index()
            if not reason_counts.empty:
                reason_counts.columns = ['Trigger Reason', 'Occurrences']
                fig_bar = px.bar(
                    reason_counts, 
                    x='Occurrences', 
                    y='Trigger Reason', 
                    orientation='h',
                    color='Occurrences',
                    color_continuous_scale=['#E4573D', '#FBE5E0']
                )
                fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
                ui_theme.style_chart(fig_bar, height=350)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.success("🎉 Zero spam triggers detected in this dataset! All reviews appear genuine.")

        st.markdown("### 🚨 Flagged Suspicious Reviews")
        suspicious_df = df[df['Is_Spam'] == True]
        if not suspicious_df.empty:
            st.dataframe(
                suspicious_df[['Spam_Reason', 'Original_Text']], 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Spam_Reason": st.column_config.TextColumn("Trigger Violation", width="medium"),
                    "Original_Text": st.column_config.TextColumn("Review Content", width="large")
                }
            )
        else:
            st.info("No suspicious reviews found.")
    else:
        st.warning("Spam detection data is not available. Ensure you are running the latest backend.")
