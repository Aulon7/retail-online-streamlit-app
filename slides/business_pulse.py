import streamlit as st
from src.data_loader import load_sales, load_cancellations


def render():
    retail_clean_df = load_sales()
    retail_cancellations_df = load_cancellations()

    st.title("Business Pulse Dashboard")

    st.subheader("Clean Retail Data Preview")
    st.dataframe(retail_clean_df.head(100), width="stretch")

    st.subheader("Cancellations Data Preview")
    st.dataframe(retail_cancellations_df.head(100), width="stretch")
