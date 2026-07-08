import streamlit as st
import pandas as pd
from src.data_loader import load_sales, filter_period, filter_country
from src.analysis import (
    total_revenue,
    total_orders,
    average_order_value,
    unique_customers,
    monthly_revenue
)
from src.charts import revenue_trend_chart

st.title("📈 Business Pulse Dashboard")
st.markdown("Track overall sales performance, monthly trends, and high-level health indicators using real dataset analysis.")

# 1. Load Real Data (Cached for speed)
try:
    df_sales = load_sales()
except Exception as e:
    st.error(f"Error loading the dataset: {e}")
    st.stop()

# 2. Sidebar Filters
st.sidebar.header("Global Filters")
unique_countries = sorted(df_sales["Country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", ["All Countries"] + unique_countries)

min_date = df_sales["InvoiceDate"].min().date()
max_date = df_sales["InvoiceDate"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply Filters
df_filtered = df_sales.copy()
df_filtered = filter_country(df_filtered, selected_country)

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    df_filtered = filter_period(df_filtered, start_date, end_date)

if df_filtered.empty:
    st.warning("No transactions found for the selected filter criteria.")
    st.stop()

# Calculate Metrics
rev = total_revenue(df_filtered)
orders = total_orders(df_filtered)
aov = average_order_value(df_filtered)
customers = unique_customers(df_filtered)

df_monthly = monthly_revenue(df_filtered)
growth_pct = 0.0
if len(df_monthly) >= 2:
    latest_month_rev = df_monthly.iloc[-1]["Revenue"]
    prev_month_rev = df_monthly.iloc[-2]["Revenue"]
    if prev_month_rev > 0:
        growth_pct = ((latest_month_rev - prev_month_rev) / prev_month_rev) * 100

# KPI Layout
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Total Revenue", 
        value=f"${rev:,.2f}",
        delta=f"{growth_pct:.1f}% vs Last Month" if len(df_monthly) >= 2 else None
    )
with col2:
    st.metric(label="Total Orders", value=f"{orders:,}")
with col3:
    st.metric(label="Average Order Value (AOV)", value=f"${aov:,.2f}")
with col4:
    st.metric(label="Active Customers", value=f"{customers:,}")

st.markdown("---")

# Monthly Trend Chart
st.subheader("Monthly Revenue Trend")
fig = revenue_trend_chart(df_filtered)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Insights
st.subheader("💡 Business Pulse Insights")
insights = []
if growth_pct > 0:
    insights.append(f"🟢 **Upward Trend:** Revenue increased by **{growth_pct:.1f}%** in the latest active month compared to the previous period.")
else:
    insights.append(f"🟡 **Sales Adjustments:** Revenue changed by **{growth_pct:.1f}%** in the latest active month. Consider reviewing seasonal buying cycles.")

if aov > 400:
    insights.append(f"⭐ **Strong Transaction Values:** The Average Order Value of **${aov:,.2f}** indicates high bulk orders or larger catalog buys.")
else:
    insights.append(f"📦 **Transaction Frequency:** The average cart checkout size is **${aov:,.2f}**. Cross-selling strategies could raise the individual basket value.")

for insight in insights:
    st.info(insight)