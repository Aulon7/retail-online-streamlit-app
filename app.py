import streamlit as st
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema
from slides import business_pulse, revenue_drivers, risk_customers

st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")

# Data validation schema for the retail dataset
RETAIL_SCHEMA = DataFrameSchema(
    {
       "Invoice": Column(str, coerce=True),
        "StockCode": Column(str, coerce=True),
        "Description": Column(str, nullable=True, coerce=True),
        "Quantity": Column(int),
        "InvoiceDate": Column("datetime64[ns]"),
        "Price": Column(float),
        "Customer ID": Column(float, nullable=True),
        "Country": Column(str, coerce=True),
    },
    strict=True,
    ordered=True,
)




def validate_schema(uploaded_file):
    """
    Validates an uploaded xlsx file against RETAIL_SCHEMA.

      1. Read only the header row and check columns match.
      2. If that passes, read the full file and run it through pandera.

    """
    try:
        header = pd.read_excel(uploaded_file, engine="calamine", nrows=0)
        uploaded_file.seek(0)

        expected_columns = list(RETAIL_SCHEMA.columns)
        if list(header.columns) != expected_columns:
            return False, f"Unexpected columns. Expected: {expected_columns}, but instead got: {list(header.columns)}"

        df = pd.read_excel(uploaded_file, engine="calamine")
        RETAIL_SCHEMA.validate(df)
        return True, "Schema verified successfully."

    except pa.errors.SchemaError as e:
        return False, f"Schema validation failed: {e}"

# Initialize Session State to remember if a valid file was uploaded
if "validated" not in st.session_state:
    st.session_state["validated"] = False

# If a valid file has not been uploaded yet, prompt the user to upload it
if st.session_state["validated"] is False:
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.title("🛍️ Online Retail Data Analysis")
        st.subheader("Please upload a dataset file to unlock insights!")

        uploaded_file = st.file_uploader(
            "Upload your data file here in xlsx format", 
            type=["xlsx"],
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            with st.spinner("Verifying file structure... please wait."):
                is_valid, message = validate_schema(uploaded_file)

            if is_valid:
                st.session_state["validated"] = True
                st.rerun()
            else:
                st.error(f"{message}")

# If validation passed, show dashboard navigation
else:
    # Navigation
    st.sidebar.title("Slides")
    slide = st.sidebar.radio(
        "Slides",
        [
            "Business Pulse Dashboard",
            "Revenue Drivers Dashboard",
            "Risk & Customer Value Dashboard",
        ],
        label_visibility="collapsed",
    )

    if slide == "Business Pulse Dashboard":
        business_pulse.render()
    elif slide == "Revenue Drivers Dashboard":
        revenue_drivers.render()
    elif slide == "Risk & Customer Value Dashboard":
        risk_customers.render()


