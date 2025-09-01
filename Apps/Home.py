import streamlit as st
import pandas as pd

st.set_page_config(page_title="Transaction Analysis App", page_icon="📊")

# --- App Title ---
st.title("📊 Paypal Transaction Analysis")

# --- Welcome Message ---
st.markdown("""
Welcome to the **Paypal Transaction Analysis App** 👋

This tool helps you explore and analyze payment transaction data with interactive visualizations and detailed breakdowns.  
Use the sidebar to navigate between different sections:
""")

# Load sample data
df = pd.read_csv("Notebooks/Data/Transactions.csv")

# Download button
st.download_button(
    label="⬇️ Download Sample Transactions Data",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="Transactions.csv",
    mime="text/csv"
)

st.info("You can download the sample CSV above and use it in the Transactions or Graphs pages.")
# --- Sections Overview ---
st.subheader("📑 Pages")
st.markdown("""
- **🛒 Transactions** →  
  Upload a CSV file of transactions and download a detailed Excel workbook containing:
  - Cleaned transaction data  
  - Summary calculations (totals, averages, refund/chargeback rates)  
  - High-ticket transactions  
  - Customer-level analysis  
  - Duplicate same-day transactions  
  - Flagged notes (raffle, lottery, etc.)

- **📈 Graphs** →  
  Visualize your transactions with:
  - Histograms of transaction amounts  
  - Monthly box & whisker plots  
  - Monthly transaction totals  
  - Monthly transaction counts  
  (with filters for status, method, source, country, and date range)
""")

# --- Footer ---
st.info("ℹ️ Tip: Start with **Transactions** to clean and prepare your data, then explore insights in **Graphs**.")
