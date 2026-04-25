import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ======================
# 1. Page Config
# ======================
st.set_page_config(
    page_title="Financial Health Analyzer",
    layout="wide"
)

# ======================
# 2. Data Loading & Engineering
# ======================
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["datadate"] = pd.to_datetime(df["datadate"], format="%Y-%m-%d", errors="coerce")
    df["year"] = df["datadate"].dt.year
    df = df[(df["year"] >= 2017) & (df["year"] <= 2026)]
    df["asset_turnover"] = df["sale"] / df["at"]
    df["asset_turnover"] = df["asset_turnover"].replace([np.inf, -np.inf], 0).fillna(0)
    df = df[df["profit_margin"].notna()]
    return df

df = load_data()

# ======================
# 3. User defined weight slider (sidebar)
# ======================
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Custom Health Score Weights")
st.sidebar.caption("Adjust weights (Total = 100%)")

w_roa = st.sidebar.slider("Profitability (ROA)", 0, 100, 40, 1)
w_debt = st.sidebar.slider("Solvency (1-Debt Ratio)", 0, 100, 30, 1)
w_margin = st.sidebar.slider("Profit Margin", 0, 100, 20, 1)
w_growth = st.sidebar.slider("Sales Growth", 0, 100, 10, 1)

total = w_roa + w_debt + w_margin + w_growth
st.sidebar.caption(f"Total weight: {total}%")

if total != 100:
    st.sidebar.warning("Total must = 100%")

# ======================
# 4. Help Text
# ======================
health_score_help = """
<div style="font-size: 11px; color: #555; line-height: 1.5; margin-bottom: 12px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;">
    <strong style="color: #333;">What is the Health Score?</strong><br>
    The Health Score is a simplified composite indicator designed to evaluate a firm's financial condition.<br>
    It combines four key dimensions:<br>
    • <strong>Profitability (ROA)</strong>: Measures how efficiently the firm generates profit from its assets<br>
    • <strong>Leverage (Debt Ratio)</strong>: Indicates financial risk (lower leverage is generally safer)<br>
    • <strong>Profit Margin</strong>: Shows how much profit is generated from revenue<br>
    • <strong>Growth (Sales Growth)</strong>: Captures the firm's expansion potential<br>
    <strong style="color: #333; margin-top: 5px; display: inline-block;">⚙️ How is it calculated?</strong><br>
    Now fully customizable by sliders in the left panel.<br>
    <em>Values are capped within a reasonable range to improve stability.</em>
</div>
"""

# ======================
# 5. Rating function: using user input weights
# ======================
def calculate_health_score(row, w1, w2, w3, w4):
    sales_growth = row["sales_growth"] if pd.notna(row["sales_growth"]) else 0
    score = (
        w1 * np.clip(row["roa"], -0.5, 0.5) +
        w2 * np.clip(1 - row["debt_ratio"], 0, 1) +
        w3 * np.clip(row["profit_margin"], -0.5, 0.5) +
        w4 * np.clip(sales_growth, -0.5, 0.5)
    )
    return score

# ======================
# 6. Diagnostic function
# ======================
def display_diagnosis(row, ticker):
    diagnosis = []
    roa, debt, margin, growth = row["roa"], row["debt_ratio"], row["profit_margin"], row["sales_growth"]
    if roa < 0: diagnosis.append("The firm is currently unprofitable, indicating inefficiency in using its assets.")
    elif roa > 0.1: diagnosis.append("The firm shows strong profitability and efficient asset utilization.")
    if debt > 0.6: diagnosis.append("The firm is highly leveraged, which increases financial risk.")
    elif debt < 0.3: diagnosis.append("The firm maintains a conservative capital structure with low debt.")
    if margin < 0: diagnosis.append("Negative profit margin suggests cost or pricing issues.")
    elif margin > 0.2: diagnosis.append("High profit margin indicates strong pricing power or cost control.")
    if pd.notna(growth):
        if growth < 0: diagnosis.append("Declining sales suggest potential contraction or demand issues.")
        elif growth > 0.1: diagnosis.append("Strong revenue growth indicates expansion potential.")
    st.write(f"**{ticker} Diagnosis:**")
    for d in diagnosis:
        st.write(f"• {d}")

# ======================
# 7. User Selection
# ======================
st.sidebar.header("Control Panel")
comparison_mode = st.sidebar.checkbox("Enable Peer Comparison Mode")
ticker_list = sorted(df["tic"].dropna().unique())

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Company A (Primary)")
    tic1 = st.selectbox("Select Company", ticker_list, key="t1")
    df1 = df[df["tic"] == tic1].sort_values("datadate")
    yr1 = st.selectbox("Select Year", df1["year"].unique()[::-1], key="y1")
    row1 = df1[df1["year"] == yr1].iloc[-1]
    score1 = calculate_health_score(row1, w_roa, w_debt, w_margin, w_growth)

row2 = None
score2 = 0
if comparison_mode:
    with col_b:
        st.subheader("Company B (Peer)")
        tic2 = st.selectbox("Select Peer", ticker_list, index=1, key="t2")
        df2 = df[df["tic"] == tic2].sort_values("datadate")
        yr2 = st.selectbox("Select Year", df2["year"].unique()[::-1], key="y2")
        row2 = df2[df2["year"] == yr2].iloc[-1]
        score2 = calculate_health_score(row2, w_roa, w_debt, w_margin, w_growth)

# ======================
# 8. Radar Chart
# ======================
st.markdown("---")
col_chart, col_stat = st.columns([2, 1])
with col_chart:
    st.subheader("📊Peer Comparison")
    categories = ['Profitability', 'Solvency', 'Efficiency', 'Margin', 'Growth']
    fig = go.Figure()
    r1 = [np.clip(row1["roa"]*5,0,1), np.clip(1-row1["debt_ratio"],0,1), np.clip(row1["asset_turnover"],0,1), np.clip(row1["profit_margin"]*2,0,1), np.clip(row1["sales_growth"]*2,0,1)]
    fig.add_trace(go.Scatterpolar(r=r1, theta=categories, fill='toself', name=tic1, line_color='#1f77b4'))
    if row2 is not None:
        r2 = [np.clip(row2["roa"]*5,0,1), np.clip(1-row2["debt_ratio"],0,1), np.clip(row2["asset_turnover"],0,1), np.clip(row2["profit_margin"]*2,0,1), np.clip(row2["sales_growth"]*2,0,1)]
        fig.add_trace(go.Scatterpolar(r=r2, theta=categories, fill='toself', name=tic2, line_color='#ff7f0e'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, height=450)
    st.plotly_chart(fig, use_container_width=True)

with col_stat:
    st.subheader("Health Score Status")
    st.markdown(health_score_help, unsafe_allow_html=True)

    st.metric(f"{tic1} Score", f"{score1:.1f}")
    if score1 >= 70: st.success("Strong financial health: profitable and stable.")
    elif score1 >= 40: st.info("Moderate condition: mixed performance.")
    else: st.error("Weak financial health: potential financial risk.")
    
    if row2 is not None:
        st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        st.metric(f"{tic2} Score", f"{score2:.1f}")
        if score2 >= 70: st.success("Strong financial health: profitable and stable.")
        elif score2 >= 40: st.info("Moderate condition: mixed performance.")
        else: st.error("Weak financial health: potential financial risk.")

# ======================
# 9. Financial Diagnosis
# ======================
st.markdown("---")
st.subheader("🔍 Financial Diagnosis")
diag_a, diag_b = st.columns(2)
with diag_a:
    display_diagnosis(row1, tic1)
with diag_b:
    if row2 is not None:
        display_diagnosis(row2, tic2)

# ======================
# 10. Indicator Explanation
# ======================
with st.expander("📖 Indicator Explanation & Definitions"):
    st.markdown("""
    - **ROA (Return on Assets)**: Measures profitability relative to total assets.
    - **Debt Ratio**: Indicates financial leverage (lower is generally safer).
    - **Profit Margin**: Profitability per unit of revenue.
    - **Sales Growth**: Captures the firm's expansion potential.
    - **Asset Turnover**: Measures efficiency in using assets to generate sales.
    """)

# ======================
# 11. Historical Trends
# ======================
st.subheader("📈 Historical Trend Analysis")
metric_to_plot = st.radio("Select Metric for Trend", ["roa", "debt_ratio", "profit_margin", "sales_growth"], horizontal=True)
if comparison_mode and row2 is not None:
    comb_df = pd.concat([df1.assign(Co=tic1), df2.assign(Co=tic2)])
    fig_t = px.line(comb_df, x="datadate", y=metric_to_plot, color="Co", markers=True)
else:
    fig_t = px.line(df1, x="datadate", y=metric_to_plot, markers=True)
st.plotly_chart(fig_t, use_container_width=True)


# ======================
# 12. Industry Benchmark
# ======================
st.markdown("---")
st.subheader("🏢 Industry Benchmark Comparison")
# Acquire basic indicators
sich1 = row1["sich"]
yr1 = row1["year"]
sich2, yr2 = None, None
if comparison_mode and row2 is not None:
    sich2 = row2["sich"]
    yr2 = row2["year"]
# Single stock mode: only display Company A
if not comparison_mode:
    industry_df = df[
        (df["sich"] == sich1) & 
        (df["year"] == yr1) &
        (df[["roa", "profit_margin", "debt_ratio"]].notna().all(axis=1))
    ].copy()
    industry_sample_count = len(industry_df)
    st.caption(f"Industry Sample Size (SIC {sich1}, Year {yr1}): {industry_sample_count} companies")
    if industry_sample_count > 0:
        industry_avg = industry_df[["roa", "profit_margin", "debt_ratio"]].mean().round(4)
        compare_data = {
            "Metric": ["ROA", "Profit Margin", "Debt Ratio"],
            f"{tic1} ({yr1})": [row1["roa"].round(4), row1["profit_margin"].round(4), row1["debt_ratio"].round(4)],
            f"Industry Avg (SIC {sich1})": [industry_avg["roa"], industry_avg["profit_margin"], industry_avg["debt_ratio"]]
        }
        compare_df = pd.DataFrame(compare_data)
        fig_bar = px.bar(
            compare_df,
            x="Metric",
            y=[col for col in compare_df.columns if col not in ["Metric"]],
            barmode="group",
            color_discrete_sequence=['#1f77b4', '#A0A0A0'],
            title=f"{tic1} vs Industry Averages (SIC {sich1}, Year {yr1})",
            labels={"value": "Value", "variable": "Category"}
        )
        fig_bar.update_traces(texttemplate='%{value:.2f}', textposition='auto')
        fig_bar.update_layout(yaxis=dict(tickformat='.2f'), height=400, title_x=0.5)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.subheader("Detailed Comparison Table")
        st.dataframe(compare_df, use_container_width=True)
    else:
        st.warning(f"No valid industry data found for SIC {sich1} (Year {yr1})")
else:
    industry_df1 = df[(df["sich"] == sich1) & (df["year"] == yr1) & (df[["roa", "profit_margin", "debt_ratio"]].notna().all(axis=1))].copy()
    industry_df2 = df[(df["sich"] == sich2) & (df["year"] == yr2) & (df[["roa", "profit_margin", "debt_ratio"]].notna().all(axis=1))].copy()
    sample1 = len(industry_df1)
    sample2 = len(industry_df2)
    compare_data = {
        "Metric": ["ROA", "Profit Margin", "Debt Ratio"],
        f"{tic1} ({yr1})": [row1["roa"].round(4), row1["profit_margin"].round(4), row1["debt_ratio"].round(4)],
        f"{tic2} ({yr2})": [row2["roa"].round(4), row2["profit_margin"].round(4), row2["debt_ratio"].round(4)]
    }
    if sich1 == sich2 and sample1>0:
        industry_avg = industry_df1[["roa", "profit_margin", "debt_ratio"]].mean().round(4)
        compare_data[f"Industry Avg (SIC {sich1})"] = [industry_avg["roa"], industry_avg["profit_margin"], industry_avg["debt_ratio"]]
    else:
        if sample1>0:
            industry_avg1 = industry_df1[["roa", "profit_margin", "debt_ratio"]].mean().round(4)
            compare_data[f"{tic1}'s Industry Avg (SIC {sich1})"] = [industry_avg1["roa"], industry_avg1["profit_margin"], industry_avg1["debt_ratio"]]
        if sample2>0:
            industry_avg2 = industry_df2[["roa", "profit_margin", "debt_ratio"]].mean().round(4)
            compare_data[f"{tic2}'s Industry Avg (SIC {sich2})"] = [industry_avg2["roa"], industry_avg2["profit_margin"], industry_avg2["debt_ratio"]]
    compare_df = pd.DataFrame(compare_data)
    fig_bar = px.bar(compare_df, x="Metric", y=[col for col in compare_df.columns if col not in ["Metric"]], barmode="group")
    fig_bar.update_traces(texttemplate='%{value:.2f}')
    st.plotly_chart(fig_bar, use_container_width=True)
    st.dataframe(compare_df, use_container_width=True)

# ======================
# 13. Industry Boxplot
# ======================
st.markdown("---")
st.subheader("📊 Industry Distribution Analysis")
box_metric = st.radio(
    "Select Metric for Industry Distribution",
    ["roa", "profit_margin", "debt_ratio", "asset_turnover"],
    horizontal=True, key="box_metric"
)
metric_names = {"roa":"ROA","profit_margin":"Profit Margin","debt_ratio":"Debt Ratio","asset_turnover":"Asset Turnover"}

# Industry Box Diagram Code
try:
    sich1 = row1["sich"]
    yr1 = row1["year"]
    if not comparison_mode:
        industry_df = df[(df["sich"]==sich1)&(df["year"]==yr1)&(df[box_metric].notna())].copy()
        if len(industry_df)>0:
            fig_box = px.box(industry_df,y=box_metric,points="outliers")
            fig_box.add_hline(y=row1[box_metric],line_dash="dash",line_color="red")
            st.plotly_chart(fig_box,use_container_width=True)
    else:
        sich2 = row2["sich"]
        yr2 = row2["year"]
        industry_df1 = df[(df["sich"]==sich1)&(df["year"]==yr1)&(df[box_metric].notna())].copy()
        industry_df2 = df[(df["sich"]==sich2)&(df["year"]==yr2)&(df[box_metric].notna())].copy()
        if sich1==sich2 and len(industry_df1)>0:
            fig_box = px.box(industry_df1,y=box_metric,points="outliers")
            fig_box.add_hline(y=row1[box_metric],line_dash="dash",line_color="red")
            fig_box.add_hline(y=row2[box_metric],line_dash="dot",line_color="orange")
            st.plotly_chart(fig_box,use_container_width=True)
        else:
            c1,c2 = st.columns(2)
            with c1:
                if len(industry_df1)>0:
                    fig1 = px.box(industry_df1,y=box_metric)
                    fig1.add_hline(y=row1[box_metric],line_dash="dash",color="red")
                    st.plotly_chart(fig1,use_container_width=True)
            with c2:
                if len(industry_df2)>0:
                    fig2 = px.box(industry_df2,y=box_metric)
                    fig2.add_hline(y=row2[box_metric],line_dash="dash",color="orange")
                    st.plotly_chart(fig2,use_container_width=True)
except:
    pass

st.caption("Data source: WRDS Compustat")
