import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from src.data_loader import load_sales
except ImportError:
    def load_sales():
        return pd.read_parquet("data/retail_clean.parquet")


def normalize_columns_local(df):
    rename_map = {
        "Customer ID": "CustomerID",
        "Customer_ID": "CustomerID",
        "customer_id": "CustomerID",
        "CustomerNo": "CustomerID",
        "Customer No": "CustomerID",
        "Invoice No": "InvoiceNo",
        "Invoice_No": "InvoiceNo",
        "invoice_no": "InvoiceNo",
        "InvoiceNumber": "InvoiceNo",
        "Invoice Number": "InvoiceNo",
        "Invoice": "InvoiceNo",
        "invoice": "InvoiceNo",
        "Unit Price": "UnitPrice",
        "Unit_Price": "UnitPrice",
        "unit_price": "UnitPrice",
        "Price": "UnitPrice",
        "price": "UnitPrice",
        "Rate": "UnitPrice",
        "Invoice Date": "InvoiceDate",
        "Invoice_Date": "InvoiceDate",
        "invoice_date": "InvoiceDate",
        "Date": "InvoiceDate",
        "date": "InvoiceDate",
    }
    return df.rename(columns=rename_map)


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


def render():
    st.title("📈 Business Pulse Dashboard")
    st.markdown("Track overall sales performance, monthly trends, and high-level health indicators using real dataset analysis.")

    try:
        df_raw = load_sales()
        df_sales = normalize_columns_local(df_raw)

        if "InvoiceDate" in df_sales.columns:
            df_sales["InvoiceDate"] = pd.to_datetime(df_sales["InvoiceDate"])

        if "Revenue" not in df_sales.columns and "Quantity" in df_sales.columns and "UnitPrice" in df_sales.columns:
            df_sales["Revenue"] = df_sales["Quantity"] * df_sales["UnitPrice"]
    except Exception as e:
        st.error(f"Error loading or preparing the dataset: {e}")
        st.stop()

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
            max_value=max_date,
        )
    else:
        selected_dates = None

    df_filtered = df_sales.copy()
    df_filtered = filter_country_local(df_filtered, selected_country)

    if selected_dates and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        df_filtered = filter_period_local(df_filtered, start_date, end_date)

    if df_filtered.empty:
        st.warning("No transactions found for the selected filter criteria.")
        st.stop()

    rev = float(df_filtered["Revenue"].sum()) if "Revenue" in df_filtered.columns else 0.0
    orders = int(df_filtered["InvoiceNo"].nunique()) if "InvoiceNo" in df_filtered.columns else 0
    aov = float(rev / orders) if orders > 0 else 0.0
    customers = int(df_filtered["CustomerID"].dropna().nunique()) if "CustomerID" in df_filtered.columns else 0

    df_monthly = pd.DataFrame(columns=["YearMonth", "Revenue"])
    if "InvoiceDate" in df_filtered.columns and "Revenue" in df_filtered.columns:
        df_temp = df_filtered.copy()
        df_temp["YearMonth"] = df_temp["InvoiceDate"].dt.to_period("M").astype(str)
        df_monthly = df_temp.groupby("YearMonth")["Revenue"].sum().reset_index().sort_values("YearMonth")

    growth_pct = 0.0
    if len(df_monthly) >= 2:
        latest_month_rev = df_monthly.iloc[-1]["Revenue"]
        prev_month_rev = df_monthly.iloc[-2]["Revenue"]
        if prev_month_rev > 0:
            growth_pct = ((latest_month_rev - prev_month_rev) / prev_month_rev) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${rev:,.2f}",
            delta=f"{growth_pct:.1f}% vs Last Month" if len(df_monthly) >= 2 else None,
        )
    with col2:
        st.metric(label="Total Orders", value=f"{orders:,}")
    with col3:
        st.metric(label="Average Order Value (AOV)", value=f"${aov:,.2f}")
    with col4:
        st.metric(label="Active Customers", value=f"{customers:,}")

    st.markdown("---")

    st.subheader("Monthly Revenue Trend")
    if not df_monthly.empty:
        fig = px.line(
            df_monthly,
            x="YearMonth",
            y="Revenue",
            title=f"Monthly Sales Performance ({selected_country})",
            labels={"YearMonth": "Month", "Revenue": "Revenue ($)"},
            markers=True,
        )
        fig.update_traces(line_color="#29B5E8", line_width=3)
        fig.update_layout(
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Trend visualization unavailable due to missing dates in the data selection.")

    st.markdown("---")

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