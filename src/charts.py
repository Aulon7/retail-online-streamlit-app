import plotly.express as px
from src.analysis import monthly_revenue, top_products, revenue_by_country, top_customers, top_returned_products

def revenue_trend_chart(df):
    df_monthly = monthly_revenue(df)
    if df_monthly.empty:
        return px.line(title="No Data Available")
    fig = px.line(df_monthly, x="YearMonth", y="Revenue", markers=True)
    fig.update_traces(line_color="#29B5E8", line_width=3)
    fig.update_layout(hovermode="x unified", template="plotly_white", margin=dict(l=10, r=10, t=10, b=10))
    return fig

# P4: Charts
def top_products_chart(df):
    """Creates horizontal bar chart for top products."""
    df_top = top_products(df, n=10)
    if df_top.empty:
        return px.bar(title="No Data")
    fig = px.bar(
        df_top.sort_values("Revenue", ascending=True),
        x="Revenue",
        y="Description",
        orientation="h",
        title="Top 10 Products by Revenue"
    )
    fig.update_traces(marker_color="#29B5E8")
    fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
    return fig

def revenue_country_chart(df):
    """Creates a bar chart comparing revenue by country (excluding United Kingdom for scale)."""
    df_country = revenue_by_country(df)
    # Exclude UK because it dwarfs other countries
    df_filtered = df_country[df_country["Country"] != "United Kingdom"].head(10)
    if df_filtered.empty:
        return px.bar(title="No International Sales Data")
    fig = px.bar(
        df_filtered,
        x="Country",
        y="Revenue",
        title="Top 10 International Markets (Excl. UK)"
    )
    fig.update_traces(marker_color="#2B4C7E")
    fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
    return fig

# P5: Charts
def returns_chart(df_returns):
    """Creates a vertical bar chart of top returned products."""
    df_returned = top_returned_products(df_returns, n=10)
    if df_returned.empty:
        return px.bar(title="No Returns Data Available")
    fig = px.bar(
        df_returned,
        x="Description",
        y="Quantity",
        title="Top 10 Returned Products by Volume"
    )
    fig.update_traces(marker_color="#E05A47")
    fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
    return fig

def customer_chart(df):
    """Creates horizontal bar chart of top spenders."""
    df_cust = top_customers(df, n=10)
    if df_cust.empty:
        return px.bar(title="No Customer Data")
    fig = px.bar(
        df_cust.sort_values("Revenue", ascending=True),
        x="Revenue",
        y="CustomerID",
        orientation="h",
        title="Top 10 Customers by Spend"
    )
    fig.update_traces(marker_color="#5D6D7E")
    fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
    return fig