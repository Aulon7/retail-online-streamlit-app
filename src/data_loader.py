"""Utilities for loading and filtering dashboard datasets."""

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SALES_PATH = DATA_DIR / "retail_clean.parquet"
RETURNS_PATH = DATA_DIR / "retail_cancellations.parquet"


def _copy_with_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with InvoiceDate parsed as datetime."""
    frame = df.copy()
    if "InvoiceDate" in frame.columns:
        frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce")
    return frame


def _is_all_selection(value) -> bool:
    """Return True when the filter should be treated as unfiltered."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == "" or value == "All"
    if isinstance(value, (list, tuple, set)):
        if len(value) == 0:
            return True
        return "All" in value
    return False


def _normalize_selection(value):
    """Normalize a scalar or iterable selection into a list."""
    if _is_all_selection(value):
        return None
    if isinstance(value, (list, tuple, set)):
        return [item for item in value if item not in (None, "", "All")]
    return [value]


@st.cache_data
def load_sales() -> pd.DataFrame:
    """Load the cleaned sales dataset from parquet."""
    df = _copy_with_datetime(pd.read_parquet(SALES_PATH))
    if "Revenue" not in df.columns:
        df["Revenue"] = df["Quantity"] * df["Price"]
    return df


@st.cache_data
def load_returns() -> pd.DataFrame:
    """Load the cleaned returns dataset from parquet."""
    df = _copy_with_datetime(pd.read_parquet(RETURNS_PATH))
    df["ReturnValue"] = (df["Quantity"] * df["Price"]).abs()
    df["ReturnQuantity"] = df["Quantity"].abs()
    return df


def filter_period(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """Filter rows by InvoiceDate within an optional date range."""
    if df.empty or "InvoiceDate" not in df.columns:
        return df.copy()

    mask = pd.Series(True, index=df.index)
    if start_date is not None:
        mask &= df["InvoiceDate"] >= pd.to_datetime(start_date)
    if end_date is not None:
        mask &= df["InvoiceDate"] <= pd.to_datetime(end_date)
    return df.loc[mask].copy()


def filter_country(df: pd.DataFrame, countries=None) -> pd.DataFrame:
    """Filter rows by country selection."""
    selected = _normalize_selection(countries)
    if selected is None or "Country" not in df.columns:
        return df.copy()
    return df[df["Country"].isin(selected)].copy()


def filter_product(df: pd.DataFrame, products=None) -> pd.DataFrame:
    """Filter rows by StockCode selection."""
    selected = _normalize_selection(products)
    if selected is None or "StockCode" not in df.columns:
        return df.copy()
    return df[df["StockCode"].isin(selected)].copy()


def filter_customer(df: pd.DataFrame, customers=None) -> pd.DataFrame:
    """Filter rows by customer selection."""
    selected = _normalize_selection(customers)
    if selected is None or "Customer ID" not in df.columns:
        return df.copy()
    return df[df["Customer ID"].isin(selected)].copy()

def load_cancellations():
    """Backward-compatible alias for load_returns."""
    return load_returns()

def apply_filters(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    countries=None,
    products=None,
    customers=None,
) -> pd.DataFrame:
    """Apply dashboard filters in a predictable order."""
    filtered = filter_period(df, start_date=start_date, end_date=end_date)
    filtered = filter_country(filtered, countries=countries)
    filtered = filter_product(filtered, products=products)
    filtered = filter_customer(filtered, customers=customers)
    return filtered
