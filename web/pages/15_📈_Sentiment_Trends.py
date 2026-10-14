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

st.set_page_config(page_title="Sentiment Trends | ReviewPulse", page_icon="📈", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Sentiment Trends Over Time",
    subtitle="Tracks historical customer perception, satisfaction trajectory, and monthly polarity swings to detect seasonal or product update impacts.",
    icon="📈"
)

if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Sentiment Trends Over Time")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)
    
    if 'Date' in df.columns and df['Date'].astype(str).str.strip().any() and not df['Date'].astype(str).str.strip().eq("None").all():
        try:
            df = df[df['Date'].astype(str).str.strip() != "None"]
            df = df[df['Date'].astype(str).str.strip() != ""]
            
            df['Parsed_Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Parsed_Date'])
            
            if not df.empty:
                df['Month_Year'] = df['Parsed_Date'].dt.to_period('M').astype(str)
                trend_df = df.groupby(['Month_Year', 'Sentiment_Label']).size().reset_index(name='Count')
                
                st.markdown("### 📊 Monthly Sentiment Trajectory")
                fig = px.line(
                    trend_df, 
                    x='Month_Year', 
                    y='Count', 
                    color='Sentiment_Label', 
                    markers=True,
                    color_discrete_map={'Positive':'#10b981', 'Neutral':'#7FA3EC', 'Negative':'#E4573D'},
                    title="Review Volume by Sentiment Over Time"
                )
                fig.update_layout(xaxis_title="Timeline (Year-Month)", yaxis_title="Review Count")
                ui_theme.style_chart(fig, height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 📋 Monthly Sentiment Proportions")
                pivot_df = trend_df.pivot(index='Month_Year', columns='Sentiment_Label', values='Count').fillna(0)
                pivot_df['Total'] = pivot_df.sum(axis=1)
                
                for col in ['Positive', 'Neutral', 'Negative']:
                    if col in pivot_df.columns:
                        pivot_df[f"{col} %"] = (pivot_df[col] / pivot_df['Total'] * 100).round(1).astype(str) + "%"
                        
                st.dataframe(pivot_df.drop(columns=['Total']), use_container_width=True)
            else:
                st.error("No valid calendar dates could be parsed from the provided Date column.")
        except Exception as e:
            st.error(f"Error parsing dates: {e}")
    else:
        st.info("ℹ️ No Date column was provided during upload. To explore temporal sentiment trends, upload a file containing a timestamp/date column or load our sample dataset.")
        if st.button("🚀 Load Sample Dataset with Dates", type="primary", key="load_sample_trends"):
            with st.spinner("Analyzing sample dataset... ☕"):
                s_df = analyzer_service.get_sample_dataset()
                res = analyzer_service.run_analysis_local(s_df, "Review_Text", "Date")
                st.session_state['results'] = res
                st.session_state['dataset_name'] = "Sample E-Commerce Reviews"
                st.rerun()
