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

st.set_page_config(page_title="Sentiment Analysis | ReviewPulse", page_icon="😊", layout="wide")
ui_theme.apply_theme()

ui_theme.render_page_header(
    title="Sentiment Analysis",
    subtitle="Classifies customer emotions and tone across reviews into Positive, Neutral, or Negative categories using calibrated VADER compound polarity scoring.",
    icon="😊"
)

# ------------------------------------------------------------------
# Interactive Live Sandbox
# ------------------------------------------------------------------
with st.expander("🧪 Try Live Sentiment Tester Sandbox", expanded=False):
    sent_test = st.text_input(
        "Enter any sentence or review to calculate real-time polarity:",
        value="The customer support team was incredibly helpful and resolved my issue within minutes!"
    )
    if st.button("⚡ Score Sentiment", type="primary", key="btn_sent_test"):
        try:
            from nlp_processor import analyze_sentiment
            s_res = analyze_sentiment(sent_test)
            label = s_res['label']
            score = s_res['compound']
            sc1, sc2, sc3 = st.columns([1.5, 1.5, 1])
            with sc1:
                if label == "Positive":
                    st.success(f"Sentiment: **Positive** 😊")
                elif label == "Negative":
                    st.error(f"Sentiment: **Negative** 😡")
                else:
                    st.info(f"Sentiment: **Neutral** 😐")
            with sc2:
                st.metric("Compound Score", f"{score:+.3f}", help="Ranges from -1.0 (very negative) to +1.0 (very positive)")
            with sc3:
                norm_score = int(((score + 1) / 2) * 100)
                st.metric("Positivity Index", f"{norm_score}/100")
        except Exception as e:
            st.error(f"Sentiment scoring error: {e}")

# ------------------------------------------------------------------
# Dataset-driven Sentiment Analysis
# ------------------------------------------------------------------
if 'results' not in st.session_state or 'processed_data' not in st.session_state['results']:
    ui_theme.render_no_data_warning("Sentiment Analysis")
else:
    data = st.session_state['results']['processed_data']
    df = pd.DataFrame(data)
    total_revs = len(df)
    
    # Calculate distribution
    counts = df['Sentiment_Label'].value_counts()
    pos_count = counts.get('Positive', 0)
    neu_count = counts.get('Neutral', 0)
    neg_count = counts.get('Negative', 0)
    
    pos_pct = (pos_count / total_revs * 100) if total_revs > 0 else 0
    neu_pct = (neu_count / total_revs * 100) if total_revs > 0 else 0
    neg_pct = (neg_count / total_revs * 100) if total_revs > 0 else 0
    nss = pos_pct - neg_pct
    
    st.markdown("### 📊 Dataset Sentiment KPIs")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Reviews", f"{total_revs:,}")
    m2.metric("Positive Reviews", f"{pos_pct:.1f}%", f"{pos_count} reviews")
    m3.metric("Neutral Reviews", f"{neu_pct:.1f}%", f"{neu_count} reviews")
    m4.metric("Negative Reviews", f"{neg_pct:.1f}%", f"-{neg_count} reviews", delta_color="inverse")
    m5.metric("Net Sentiment Score", f"{nss:+.1f}", help="Net Sentiment = % Positive - % Negative")

    st.markdown("### 📈 Visual Distribution")
    col_chart1, col_chart2 = st.columns([1, 1.2])
    
    with col_chart1:
        sentiment_counts = pd.DataFrame({
            "Sentiment": ["Positive", "Neutral", "Negative"],
            "Count": [pos_count, neu_count, neg_count]
        })
        fig_pie = px.pie(
            sentiment_counts, 
            values='Count', 
            names='Sentiment', 
            color='Sentiment',
            color_discrete_map={'Positive': '#10b981', 'Neutral': '#7FA3EC', 'Negative': '#E4573D'},
            hole=0.45,
            title="Sentiment Proportion"
        )
        ui_theme.style_chart(fig_pie, height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        if 'Sentiment_Score' in df.columns:
            fig_hist = px.histogram(
                df, 
                x='Sentiment_Score', 
                nbins=20, 
                title="Compound Polarity Score Distribution (-1 to +1)",
                color_discrete_sequence=['#2F5FD6']
            )
            fig_hist.update_layout(xaxis_title="Compound Polarity Score", yaxis_title="Review Count")
            ui_theme.style_chart(fig_hist, height=350)
            st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("### 🔍 Filtered Review Explorer")
    selected_sentiment = st.selectbox("Filter by Sentiment Label:", ["All", "Positive", "Neutral", "Negative"])
    
    filtered_df = df.copy()
    if selected_sentiment != "All":
        filtered_df = filtered_df[filtered_df['Sentiment_Label'] == selected_sentiment]
        
    st.dataframe(
        filtered_df[['Original_Text', 'Sentiment_Label', 'Sentiment_Score']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Original_Text": st.column_config.TextColumn("Customer Review", width="large"),
            "Sentiment_Label": st.column_config.TextColumn("Label", width="small"),
            "Sentiment_Score": st.column_config.NumberColumn("Polarity Score", format="%.3f", width="small")
        }
    )
