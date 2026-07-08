import streamlit as st
import pandas as pd

# Import ONLY the core data loading function from P2's backend
from src.data_loader import load_sales

# Import the analytical and chart functions from P2's backend
from src.analysis import (
    total_revenue,
    total_orders,
    average_order_value,
    unique_customers,
    monthly_revenue
)
from src.charts import revenue_trend_chart

# ------------------------------------------------------------
# LOCAL FILTERING FUNCTIONS 
# (Kept here to ensure page works independently of P2's backend)
# ------------------------------------------------------------
def filter_period_local(df, start_date, end_date):
    if "InvoiceDate" in df.columns:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        return df[(df["InvoiceDate"].dt.date >= start.date()) & (df["InvoiceDate"].dt.date <= end.date())]
    return df

def filter_country_local(df, country):
    if "Country" in df.columns and country != "All Countries":
        return df[df["Country"] == country]
    return df

# ------------------------------------------------------------
# STREAMLIT PAGE SETUP
# ------------------------------------------------------------
st.title("📈 Business Pulse Dashboard")
st.markdown("Track overall sales performance, monthly trends, and high-level health indicators using real dataset analysis.")

# 1. Load Real Data (Cached for speed)
try:
    df_sales = load_sales()
except Exception as e:
    st.error(f"Error loading the dataset from P2's backend: {e}")
    st.stop()

# 2. Sidebar Filters
st.sidebar.header("Global Filters")
unique_countries = sorted(df_sales["Country"].dropna().unique().tolist()) if "Country" in df_sales.columns else []
selected_country = st.sidebar.selectbox("Select Country", ["All Countries"] + unique_countries)

if "InvoiceDate" in df_sales.columns:
    min_date = df_sales["InvoiceDate"].min().date()
    max_date = df_sales["InvoiceDate"].max().date()

    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    selected_dates = None

# Apply local filters
df_filtered = df_sales.copy()
df_filtered = filter_country_local(df_filtered, selected_country)

if selected_dates and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    df_filtered = filter_period_local(df_filtered, start_date, end_date)

if df_filtered.empty:
    st.warning("No transactions found for the selected filter criteria.")
    st.stop()

# 3. Calculate Metrics using P2's backend
try:
    rev = total_revenue(df_filtered)
    orders = total_orders(df_filtered)
    aov = average_order_value(df_filtered)
    customers = unique_customers(df_filtered)
    df_monthly = monthly_revenue(df_filtered)
except Exception as e:
    st.error(f"Error calculating analysis metrics from P2's backend: {e}")
    st.stop()

growth_pct = 0.0
if len(df_monthly) >= 2:
    latest_month_rev = df_monthly.iloc[-1]["Revenue"]
    prev_month_rev = df_monthly.iloc[-2]["Revenue"]
    if prev_month_rev > 0:
        growth_pct = ((latest_month_rev - prev_month_rev) / prev_month_rev) * 100

# 4. KPI Layout
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
    st.metric(label="Active Cus