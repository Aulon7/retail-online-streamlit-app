import pandas as pd
import streamlit as st

def normalize_columns(df):
    """
    Safely normalizes spaced, raw, or alternate column names 
    to standardized keys for all pages and calculations.
    """
    rename_map = {
        # Customer ID variations
        "Customer ID": "CustomerID",
        "Customer_ID": "CustomerID",
        "customer_id": "CustomerID",
        "CustomerNo": "CustomerID",
        "Customer No": "CustomerID",
        
        # Invoice/Order ID variations
        "Invoice No": "InvoiceNo",
        "Invoice_No": "InvoiceNo",
        "invoice_no": "InvoiceNo",
        "InvoiceNumber": "InvoiceNo",
        "Invoice Number": "InvoiceNo",
        "Invoice": "InvoiceNo",
        "invoice": "InvoiceNo",
        
        # Unit Price variations
        "Unit Price": "UnitPrice",
        "Unit_Price": "UnitPrice",
        "unit_price": "UnitPrice",
        "Price": "UnitPrice",
        "price": "UnitPrice",
        "Rate": "UnitPrice",
        
        # Date variations
        "Invoice Date": "InvoiceDate",
        "Invoice_Date": "InvoiceDate",
        "invoice_date": "InvoiceDate",
        "Date": "InvoiceDate",
        "date": "InvoiceDate",
    }
    return df.rename(columns=rename_map)

@st.cache_data
def load_sales():
    df = pd.read_parquet("data/retail_clean.parquet")
    df = normalize_columns(df)
    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    if "Revenue" not in df.columns and "Quantity" in df.columns and "UnitPrice" in df.columns:
        df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    return df

@st.cache_data
def load_returns():
    try:
        df = pd.read_parquet("data/retail_cancellations.parquet")
        df = normalize_columns(df)
        if "InvoiceDate" in df.columns:
            df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
        if "Revenue" not in df.columns and "Quantity" in df.columns and "UnitPrice" in df.columns:
            df["Revenue"] = df["Quantity"] * df["UnitPrice"]
        return df
    except FileNotFoundError:
        return pd.DataFrame()

def filter_period(df, start_date, end_date):
    if "InvoiceDate" in df.columns:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        return df[(df["InvoiceDate"].dt.date >= start.date()) & (df["InvoiceDate"].dt.date <= end.date())]
    return df

def filter_country(df, country):
    if "Country" in df.columns and country != "All Countries":
        return df[df["Country"] == country]
    return df

# Alias to prevent import conflicts
load_cancellations = load_returns