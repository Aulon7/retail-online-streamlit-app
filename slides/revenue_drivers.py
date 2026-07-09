import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from src.data_loader import load_sales
except ImportError:
    def load_sales():
        return pd.read_parquet("data/retail_clean.parquet")


DOMESTIC_MARKET = "United Kingdom"

RENAME_MAP = {
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


def normalize_columns_local(df):
    return df.rename(columns=RENAME_MAP)


def filter_country_local(df, country):
    if "Country" in df.columns and country != "All Countries":
        return df[df["Country"] == country]
    return df


def render():
    st.title("💰 Revenue Drivers")
    st.markdown("Discover which products generate the most demand and which international markets drive growth.")

    try:
        df_raw = load_sales()
        df_sales = normalize_columns_local(df_raw)
        if "Country" in df_sales.columns:
            df_sales["Country"] = df_sales["Country"].astype(str).str.strip()
        if "Revenue" not in df_sales.columns and "Quantity" in df_sales.columns and "UnitPrice" in df_sales.columns:
            df_sales["Revenue"] = df_sales["Quantity"] * df_sales["UnitPrice"]
    except Exception as e:
        st.error(f"Error loading files: {e}")
        st.stop()

    st.sidebar.header("Global Filters")
    unique_countries = sorted(df_sales["Country"].dropna().unique().tolist()) if "Country" in df_sales.columns else []
    selected_country = st.sidebar.selectbox("Select Country", ["All Countries"] + unique_countries, key="p4_country")

    df_filtered = filter_country_local(df_sales, selected_country)

    df_top_products = pd.DataFrame(columns=["Description", "Revenue"])
    if "Description" in df_filtered.columns and "Revenue" in df_filtered.columns:
        df_top_products = df_filtered.groupby("Description")["Revenue"].sum().reset_index()
        df_top_products = df_top_products.sort_values("Revenue", ascending=False).head(10)

    df_country_sales = pd.DataFrame(columns=["Country", "Revenue"])
    if "Country" in df_filtered.columns and "Revenue" in df_filtered.columns:
        df_country_sales = df_filtered.groupby("Country")["Revenue"].sum().reset_index()
        df_country_sales = df_country_sales.sort_values("Revenue", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        if not df_top_products.empty:
            fig_prod = px.bar(
                df_top_products.sort_values("Revenue", ascending=True),
                x="Revenue",
                y="Description",
                orientation="h",
                title="Top 10 Products by Revenue",
            )
            fig_prod.update_traces(marker_color="#29B5E8")
            fig_prod.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_prod, use_container_width=True)
        else:
            st.warning("No product data available.")

    with col2:
        df_international = df_country_sales[df_country_sales["Country"] != DOMESTIC_MARKET].head(10) if not df_country_sales.empty else pd.DataFrame()
        if not df_international.empty:
            fig_country = px.bar(
                df_international,
                x="Country",
                y="Revenue",
                title="Top 10 International Markets (Excl. UK)",
            )
            fig_country.update_traces(marker_color="#2B4C7E")
            fig_country.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_country, use_container_width=True)
        else:
            st.warning("No international sales data available.")

    st.markdown("---")

    st.subheader("💡 Market Expansion Recommendations")
    if not df_country_sales.empty:
        top_countries_list = df_country_sales[df_country_sales["Country"] != DOMESTIC_MARKET].head(3)
        if not top_countries_list.empty:
            top_1 = top_countries_list.iloc[0]["Country"]
            st.success(
                f"🎯 **Key Recommendation:** Aside from the domestic UK market, **{top_1}** is your primary international driver. "
                f"Consider localizing payment processing, targeted ad campaigns, or shipping promotions specifically in this territory to increase conversions."
            )
        else:
            st.info("Domestic market dominates. Expansion analysis will populate once international sales records are logged.")
