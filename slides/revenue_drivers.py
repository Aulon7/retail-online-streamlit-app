import streamlit as st
from src.data_loader import load_sales, filter_period, filter_country
from src.charts import top_products_chart, revenue_country_chart
from src.analysis import top_products, revenue_by_country

st.title("💰 Revenue Drivers")
st.markdown("Discover which products generate the most demand and which international markets drive growth.")

# Load sales dataset
try:
    df_sales = load_sales()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# Filter Controls (Sidebar is shared)
st.sidebar.header("Global Filters")
unique_countries = sorted(df_sales["Country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", ["All Countries"] + unique_countries, key="p4_country")

df_filtered = filter_country(df_sales, selected_country)

# Visualizations in two columns
col1, col2 = st.columns(2)

with col1:
    fig_prod = top_products_chart(df_filtered)
    st.plotly_chart(fig_prod, use_container_width=True)

with col2:
    fig_country = revenue_country_chart(df_filtered)
    st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

# Recommendations Insight Box
st.subheader("💡 Market Expansion Recommendations")
top_countries_list = revenue_by_country(df_filtered)[revenue_by_country(df_filtered)["Country"] != "United Kingdom"].head(3)

if not top_countries_list.empty:
    top_1 = top_countries_list.iloc[0]["Country"]
    st.success(
        f"🎯 **Key Recommendation:** Aside from the domestic UK market, **{top_1}** is your primary international driver. "
        f"Consider localizing payment processing, targeted ad campaigns, or shipping promotions specifically in this territory to increase conversions."
    )
else:
    st.info("Domestic market dominates. Expansion analysis will populate once international sales records are logged.")