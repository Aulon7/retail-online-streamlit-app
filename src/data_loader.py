import streamlit as st
import pandas as pd


@st.cache_data
def load_sales():
    return pd.read_parquet("data/retail_clean.parquet")


@st.cache_data
def load_cancellations():
    return pd.read_parquet("data/retail_cancellations.parquet")
