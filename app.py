import streamlit as st

# Configure the main entry page
st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Sales Intelligence Dashboard")
st.markdown("---")

st.markdown("""
### Welcome, Sales Manager!
This interactive dashboard is designed to provide quick, data-driven answers to three major business questions:

1. **How is the business performing?**
2. **What products and markets generate the most revenue?**
3. **Where are the biggest risks and who are our most valuable customers?**

---

### 🗺️ How to Navigate the Dashboard
Use the sidebar on the left-hand side to switch between pages:

*   **📈 Business Pulse:** High-level performance KPIs, monthly revenue growth trends, and automated business health insights.
*   **🚗 Revenue Drivers:** Deep-dive into top-selling products, regional performance, and average order values by country.
*   **⚠️ Risk & Customer Value:** Analysis of returned/cancelled products, customer value concentrations, and customer loyalty rankings.
""")

# Optional project team credit footer
st.markdown("---")
st.caption("Developed as part of Project 2 -- Automated Reporting Dashboard Team.")