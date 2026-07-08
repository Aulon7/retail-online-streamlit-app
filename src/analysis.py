import pandas as pd

# Core sales metrics
def total_revenue(df):
    return float(df["Revenue"].sum()) if "Revenue" in df.columns else 0.0

def total_orders(df):
    if "InvoiceNo" in df.columns:
        return int(df["InvoiceNo"].nunique())
    return 0

def average_order_value(df):
    rev = total_revenue(df)
    orders = total_orders(df)
    return float(rev / orders) if orders > 0 else 0.0

def unique_customers(df):
    if "CustomerID" in df.columns:
        return int(df["CustomerID"].dropna().nunique())
    return 0

def monthly_revenue(df):
    if "InvoiceDate" in df.columns and "Revenue" in df.columns:
        df_temp = df.copy()
        df_temp["YearMonth"] = df_temp["InvoiceDate"].dt.to_period("M").astype(str)
        monthly = df_temp.groupby("YearMonth")["Revenue"].sum().reset_index()
        return monthly.sort_values("YearMonth")
    return pd.DataFrame(columns=["YearMonth", "Revenue"])

# P4: Revenue Drivers metrics
def top_products(df, n=10):
    if "Description" in df.columns and "Revenue" in df.columns:
        product_sales = df.groupby("Description")["Revenue"].sum().reset_index()
        return product_sales.sort_values("Revenue", ascending=False).head(n)
    return pd.DataFrame()

def revenue_by_country(df):
    if "Country" in df.columns and "Revenue" in df.columns:
        country_sales = df.groupby("Country")["Revenue"].sum().reset_index()
        return country_sales.sort_values("Revenue", ascending=False)
    return pd.DataFrame()

# P5: Risk & Customer Value metrics
def top_customers(df, n=10):
    if "CustomerID" in df.columns and "Revenue" in df.columns:
        df_clean = df.dropna(subset=["CustomerID"])
        customer_spend = df_clean.groupby("CustomerID")["Revenue"].sum().reset_index()
        # Convert float Customer IDs safely to integers, then strings
        customer_spend["CustomerID"] = customer_spend["CustomerID"].astype(float).astype(int).astype(str)
        return customer_spend.sort_values("Revenue", ascending=False).head(n)
    return pd.DataFrame()

def revenue_concentration(df):
    if "CustomerID" in df.columns and "Revenue" in df.columns:
        df_clean = df.dropna(subset=["CustomerID"])
        cust_sales = df_clean.groupby("CustomerID")["Revenue"].sum().sort_values(ascending=False)
        if len(cust_sales) == 0:
            return 0.0
        top_10_percent_count = max(1, int(len(cust_sales) * 0.1))
        top_10_revenue = cust_sales.head(top_10_percent_count).sum()
        total_rev = cust_sales.sum()
        return float((top_10_revenue / total_rev) * 100) if total_rev > 0 else 0.0
    return 0.0

def return_rate(df_sales, df_returns):
    sales_val = total_revenue(df_sales)
    # Use abs() because returns/cancellations revenue is negative in the raw files
    returns_val = abs(total_revenue(df_returns))
    return float((returns_val / sales_val) * 100) if sales_val > 0 else 0.0

def top_returned_products(df_returns, n=10):
    if not df_returns.empty and "Description" in df_returns.columns and "Quantity" in df_returns.columns:
        returned = df_returns.groupby("Description")["Quantity"].sum().reset_index()
        # Convert negative return quantities to positive counts for visual bar charts
        returned["Quantity"] = returned["Quantity"].abs()
        return returned.sort_values("Quantity", ascending=False).head(n)
    return pd.DataFrame()