"""Business metrics for the retail reporting dashboard."""

import numpy as np
import pandas as pd


def _safe_revenue(df: pd.DataFrame) -> pd.Series:
    """Return a numeric revenue series, defaulting to zeros."""
    if "Revenue" in df.columns:
        return pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)
    if {"Quantity", "Price"}.issubset(df.columns):
        return (
            pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
            * pd.to_numeric(df["Price"], errors="coerce").fillna(0)
        )
    return pd.Series(0.0, index=df.index, dtype="float64")


def _known_customers(df: pd.DataFrame) -> pd.Series:
    """Return known customer IDs only."""
    if "Customer ID" not in df.columns:
        return pd.Series(dtype="float64")
    return df["Customer ID"].dropna()


def _product_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return the most common description for each StockCode."""
    if df.empty or not {"StockCode", "Description"}.issubset(df.columns):
        return pd.DataFrame(columns=["StockCode", "Description"])

    names = (
        df.dropna(subset=["StockCode"])
        .groupby("StockCode")["Description"]
        .agg(
            lambda values: values.dropna().mode().iloc[0]
            if not values.dropna().empty
            else ""
        )
        .reset_index()
    )
    return names


def total_revenue(df: pd.DataFrame) -> float:
    """Return total sales revenue."""
    return float(_safe_revenue(df).sum()) if not df.empty else 0.0


def total_orders(df: pd.DataFrame) -> int:
    """Return the number of unique invoices."""
    if df.empty or "Invoice" not in df.columns:
        return 0
    return int(df["Invoice"].nunique())


def average_order_value(df: pd.DataFrame) -> float:
    """Return revenue divided by unique invoice count."""
    orders = total_orders(df)
    if orders == 0:
        return 0.0
    return float(total_revenue(df) / orders)


def unique_customers(df: pd.DataFrame) -> int:
    """Return the number of known customers."""
    return int(_known_customers(df).nunique())


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by calendar month."""
    if df.empty or "InvoiceDate" not in df.columns:
        return pd.DataFrame(columns=["Month", "Revenue"])

    monthly = (
        df.assign(
            Month=pd.to_datetime(df["InvoiceDate"], errors="coerce").dt.to_period("M").dt.to_timestamp(),
            Revenue=_safe_revenue(df),
        )
        .dropna(subset=["Month"])
        .groupby("Month", as_index=False)["Revenue"]
        .sum()
        .sort_values("Month")
    )
    return monthly


def monthly_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate month-over-month revenue growth percentage."""
    monthly = monthly_revenue(df)
    if monthly.empty:
        return pd.DataFrame(columns=["Month", "Revenue", "GrowthPct"])

    monthly["GrowthPct"] = monthly["Revenue"].pct_change().replace([np.inf, -np.inf], np.nan) * 100
    monthly["GrowthPct"] = monthly["GrowthPct"].fillna(0)
    return monthly


def revenue_by_country(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return top countries ranked by revenue."""
    if df.empty or "Country" not in df.columns:
        return pd.DataFrame(columns=["Country", "Revenue"])

    result = (
        df.assign(Revenue=_safe_revenue(df))
        .groupby("Country", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(limit)
    )
    return result


def average_order_value_by_country(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return top countries ranked by average order value."""
    if df.empty or not {"Country", "Invoice"}.issubset(df.columns):
        return pd.DataFrame(columns=["Country", "Revenue", "Orders", "AOV"])

    grouped = (
        df.assign(Revenue=_safe_revenue(df))
        .groupby("Country")
        .agg(Revenue=("Revenue", "sum"), Orders=("Invoice", "nunique"))
        .reset_index()
    )
    grouped["AOV"] = np.where(grouped["Orders"] > 0, grouped["Revenue"] / grouped["Orders"], 0.0)
    return grouped.sort_values("AOV", ascending=False).head(limit)


def top_products(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return top products by revenue using StockCode as key."""
    if df.empty or "StockCode" not in df.columns:
        return pd.DataFrame(columns=["StockCode", "Description", "Revenue", "Quantity", "Orders"])

    products = (
        df.assign(Revenue=_safe_revenue(df))
        .groupby("StockCode")
        .agg(Revenue=("Revenue", "sum"), Quantity=("Quantity", "sum"), Orders=("Invoice", "nunique"))
        .reset_index()
    )
    products = products.merge(_product_names(df), on="StockCode", how="left")
    return products.sort_values("Revenue", ascending=False).head(limit)


def top_customers(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return top customers by revenue."""
    if df.empty or "Customer ID" not in df.columns:
        return pd.DataFrame(columns=["Customer ID", "Revenue", "Orders", "AOV"])

    known = df[df["Customer ID"].notna()].copy()
    if known.empty:
        return pd.DataFrame(columns=["Customer ID", "Revenue", "Orders", "AOV"])

    customers = (
        known.assign(Revenue=_safe_revenue(known))
        .groupby("Customer ID")
        .agg(Revenue=("Revenue", "sum"), Orders=("Invoice", "nunique"))
        .reset_index()
    )
    customers["AOV"] = np.where(customers["Orders"] > 0, customers["Revenue"] / customers["Orders"], 0.0)
    return customers.sort_values("Revenue", ascending=False).head(limit)


def return_rate(sales_df: pd.DataFrame, returns_df: pd.DataFrame) -> float:
    """Return returned value as a percentage of sales revenue."""
    sales_revenue = total_revenue(sales_df)
    if sales_revenue == 0:
        return 0.0
    if returns_df.empty or "ReturnValue" not in returns_df.columns:
        return 0.0
    returned_value = pd.to_numeric(returns_df["ReturnValue"], errors="coerce").fillna(0).sum()
    return float((returned_value / sales_revenue) * 100)


def top_returned_products(returns_df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return top returned products by return value."""
    if returns_df.empty or "StockCode" not in returns_df.columns:
        return pd.DataFrame(columns=["StockCode", "Description", "ReturnQuantity", "ReturnValue"])

    products = (
        returns_df.groupby("StockCode")
        .agg(ReturnQuantity=("ReturnQuantity", "sum"), ReturnValue=("ReturnValue", "sum"))
        .reset_index()
    )
    products = products.merge(_product_names(returns_df), on="StockCode", how="left")
    return products.sort_values("ReturnValue", ascending=False).head(limit)


def monthly_returns(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate returns by calendar month."""
    if returns_df.empty or "InvoiceDate" not in returns_df.columns:
        return pd.DataFrame(columns=["Month", "ReturnValue", "ReturnQuantity"])

    monthly = (
        returns_df.assign(
            Month=pd.to_datetime(returns_df["InvoiceDate"], errors="coerce").dt.to_period("M").dt.to_timestamp()
        )
        .dropna(subset=["Month"])
        .groupby("Month", as_index=False)[["ReturnValue", "ReturnQuantity"]]
        .sum()
        .sort_values("Month")
    )
    return monthly


def revenue_concentration(df: pd.DataFrame) -> pd.DataFrame:
    """Return customer revenue concentration with cumulative share."""
    if df.empty or "Customer ID" not in df.columns:
        return pd.DataFrame(columns=["Customer ID", "Revenue", "RevenueShare", "CumulativeShare"])

    customers = top_customers(df, limit=len(df))
    if customers.empty:
        return pd.DataFrame(columns=["Customer ID", "Revenue", "RevenueShare", "CumulativeShare"])

    total = customers["Revenue"].sum()
    if total == 0:
        customers["RevenueShare"] = 0.0
        customers["CumulativeShare"] = 0.0
        return customers[["Customer ID", "Revenue", "RevenueShare", "CumulativeShare"]]

    customers = customers.sort_values("Revenue", ascending=False).reset_index(drop=True)
    customers["RevenueShare"] = (customers["Revenue"] / total) * 100
    customers["CumulativeShare"] = customers["RevenueShare"].cumsum()
    return customers[["Customer ID", "Revenue", "RevenueShare", "CumulativeShare"]]


def generate_business_insights(sales_df: pd.DataFrame, returns_df: pd.DataFrame) -> list[str]:
    """Generate short headline insights from current metrics."""
    insights = []

    revenue = total_revenue(sales_df)
    orders = total_orders(sales_df)
    customers = unique_customers(sales_df)
    rate = return_rate(sales_df, returns_df)

    insights.append(f"Total revenue is {revenue:,.2f} across {orders:,} orders.")
    insights.append(f"Known active customers: {customers:,}.")
    insights.append(f"Average order value is {average_order_value(sales_df):,.2f}.")
    insights.append(f"Return rate is {rate:.2f}% of sales revenue.")

    top_country = revenue_by_country(sales_df, limit=1)
    if not top_country.empty:
        row = top_country.iloc[0]
        insights.append(f"Top market by revenue is {row['Country']} at {row['Revenue']:,.2f}.")

    top_product = top_products(sales_df, limit=1)
    if not top_product.empty:
        row = top_product.iloc[0]
        label = row["Description"] if row["Description"] else row["StockCode"]
        insights.append(f"Top product is {label} ({row['StockCode']}) with {row['Revenue']:,.2f} revenue.")

    growth = monthly_growth(sales_df)
    if len(growth) >= 2:
        latest = growth.iloc[-1]
        insights.append(f"Latest monthly growth is {latest['GrowthPct']:.2f}% in {latest['Month']:%Y-%m}.")

    return insights
