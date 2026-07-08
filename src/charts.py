"""Plotly Express chart builders for dashboard visuals."""

import pandas as pd
import plotly.express as px


def _empty_figure(title: str):
    """Return a lightweight empty figure with a title."""
    fig = px.scatter(title=title)
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    return fig


def revenue_trend_chart(monthly_df: pd.DataFrame):
    """Return a monthly revenue line chart."""
    if monthly_df.empty:
        return _empty_figure("Monthly Revenue Trend")
    return px.line(monthly_df, x="Month", y="Revenue", markers=True, title="Monthly Revenue Trend")


def top_products_chart(products_df: pd.DataFrame):
    """Return a top products revenue bar chart."""
    if products_df.empty:
        return _empty_figure("Top Products")
    labels = products_df["StockCode"].astype(str)
    if "Description" in products_df.columns:
        labels = products_df["Description"].fillna("").where(
            products_df["Description"].fillna("").str.strip() != "",
            products_df["StockCode"].astype(str),
        )
    chart_df = products_df.assign(ProductLabel=labels)
    return px.bar(chart_df, x="Revenue", y="ProductLabel", orientation="h", title="Top Products by Revenue")


def revenue_country_chart(country_df: pd.DataFrame):
    """Return a country revenue bar chart."""
    if country_df.empty:
        return _empty_figure("Revenue by Country")
    return px.bar(country_df, x="Revenue", y="Country", orientation="h", title="Revenue by Country")


def aov_country_chart(country_df: pd.DataFrame):
    """Return a country AOV bar chart."""
    if country_df.empty:
        return _empty_figure("Average Order Value by Country")
    return px.bar(country_df, x="AOV", y="Country", orientation="h", title="Average Order Value by Country")


def returns_chart(returns_df: pd.DataFrame):
    """Return a monthly returns line chart."""
    if returns_df.empty:
        return _empty_figure("Monthly Returns")
    return px.line(returns_df, x="Month", y="ReturnValue", markers=True, title="Monthly Returns")


def returned_products_chart(products_df: pd.DataFrame):
    """Return a top returned products bar chart."""
    if products_df.empty:
        return _empty_figure("Top Returned Products")
    labels = products_df["StockCode"].astype(str)
    if "Description" in products_df.columns:
        labels = products_df["Description"].fillna("").where(
            products_df["Description"].fillna("").str.strip() != "",
            products_df["StockCode"].astype(str),
        )
    chart_df = products_df.assign(ProductLabel=labels)
    return px.bar(chart_df, x="ReturnValue", y="ProductLabel", orientation="h", title="Top Returned Products")


def customer_chart(customers_df: pd.DataFrame):
    """Return a top customers revenue bar chart."""
    if customers_df.empty:
        return _empty_figure("Top Customers")
    chart_df = customers_df.assign(CustomerLabel=customers_df["Customer ID"].astype(str))
    return px.bar(chart_df, x="Revenue", y="CustomerLabel", orientation="h", title="Top Customers by Revenue")


def revenue_concentration_chart(concentration_df: pd.DataFrame):
    """Return a cumulative revenue concentration chart."""
    if concentration_df.empty:
        return _empty_figure("Revenue Concentration")
    chart_df = concentration_df.reset_index(drop=True).assign(CustomerRank=lambda df: df.index + 1)
    return px.line(
        chart_df,
        x="CustomerRank",
        y="CumulativeShare",
        markers=True,
        title="Revenue Concentration",
    )
