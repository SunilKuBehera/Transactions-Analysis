import altair as alt
import pandas as pd
import streamlit as st
import datetime
from datetime import date, timedelta
import os

# ---- Page Setup ----
st.set_page_config(page_title="Charts", page_icon="📈")
st.title("Chart Maker")

# ---- Filters ----
PaymentStatus = st.selectbox(
    'What Payment Status Would You Like to See',
    ('All', 'Charge', 'Refund', 'Chargeback')
)

PaymentMethod = st.selectbox(
    'What Payment Method Would You Like to See',
    ['All', 'Goods and Services', 'Friends & Family']
)

PaymentApplication = st.selectbox(
    'What Payment Application Would You Like to See',
    ['All', 'Desktop', 'Tablet', 'Phone']
)

PaymentCountry = st.selectbox(
    'What Payment Country Would You Like to See',
    ('All', 'US', 'UK', 'AU')
)

today = datetime.datetime.now()
days180 = date.today() - timedelta(days=180)
StartDate = st.date_input("Start Date (Default 180 Days Prior)", days180)
EndDate = st.date_input("End Date", today)

# ---- File Upload ----
st.info("ℹ️ Note: Make sure you have downloaded the **'Transactions.csv'** file from the Home page.")
uploaded = st.file_uploader("Upload transactions file", type=["csv", "xlsx"])
if uploaded is not None:
    ext = os.path.splitext(uploaded.name)[1].lower()
    if ext == ".csv":
        try:
            dfPreClean = pd.read_csv(uploaded, encoding="utf-8", on_bad_lines="skip")
        except UnicodeDecodeError:
            uploaded.seek(0)
            dfPreClean = pd.read_csv(uploaded, encoding="latin1", on_bad_lines="skip")
    elif ext == ".xlsx":
        dfPreClean = pd.read_excel(uploaded)
    else:
        st.error("Unsupported file format")
        st.stop()
else:
    st.stop()

# ---- Clean ----
dfPreClean.drop(['Transaction_ID', 'Auth_code'], axis=1, inplace=True, errors='ignore')
dfPreClean = dfPreClean[dfPreClean["Success"] == 1]
dfPreClean["Transaction_Notes"].fillna("N/A", inplace=True)
dfPreClean['Day'] = pd.to_datetime(dfPreClean['Day'], errors='coerce')
dfPreClean['Total'] = pd.to_numeric(dfPreClean['Total'], errors='coerce')

df = dfPreClean.loc[:, [
    'Total', 'Transaction_Type', 'Type', 'Country', 'Source',
    'Day', 'Customer_Name', 'Transaction_Notes'
]]
df['int_created_date'] = df['Day'].dt.strftime("%Y-%m")

# ---- Filters ----
if PaymentStatus != 'All':
    df = df[df['Type'] == PaymentStatus]

if PaymentMethod != 'All':
    df = df[df['Transaction_Type'] == PaymentMethod]

if PaymentApplication != 'All':
    df = df[df['Source'] == PaymentApplication]

if PaymentCountry != 'All':
    df = df[df['Country'] == PaymentCountry]

StartDate = pd.to_datetime(StartDate)
EndDate = pd.to_datetime(EndDate)
df = df[(df['Day'] >= StartDate) & (df['Day'] <= EndDate)]

# ---- Drop NaNs in key columns ----
df = df.dropna(subset=['Total', 'Day', 'int_created_date'])

# ---- Charts ----
if df.empty:
    st.warning("No data available for the selected filters.")
else:
    chart1 = alt.Chart(df).mark_bar().encode(
        alt.X("Total:Q", bin=True),
        y='count()',
    ).properties(
        title={
            "text": ["Histogram of Transaction Amounts"],
            "subtitle": [f"Filters → Status: {PaymentStatus}, Method: {PaymentMethod}, "
                         f"App: {PaymentApplication}, Country: {PaymentCountry}, "
                         f"Dates: {StartDate.date()} to {EndDate.date()}"],
        },
        width=800,
        height=500
    )

    chart2 = alt.Chart(df).mark_boxplot(extent='min-max').encode(
        x='int_created_date:O',
        y='Total:Q'
    ).properties(
        title={
            "text": ["Monthly Transaction Distribution (Box & Whisker)"],
            "subtitle": [f"Filters → Status: {PaymentStatus}, Method: {PaymentMethod}, "
                         f"App: {PaymentApplication}, Country: {PaymentCountry}, "
                         f"Dates: {StartDate.date()} to {EndDate.date()}"],
        },
        width=800,
        height=500
    )

    chart3 = alt.Chart(df).mark_bar().encode(
        x=alt.X('int_created_date:O', title='Month'),
        y=alt.Y('sum(Total):Q', title='Total Amount'),
        color=alt.Color('Type:N', title='Payment Type')
    ).properties(
        title={
            "text": ["Monthly Total Transaction Volume"],
            "subtitle": [f"Filters → Status: {PaymentStatus}, Method: {PaymentMethod}, "
                         f"App: {PaymentApplication}, Country: {PaymentCountry}, "
                         f"Dates: {StartDate.date()} to {EndDate.date()}"],
        },
        width=800,
        height=500
    )

    chart4 = alt.Chart(df).mark_bar().encode(
        x=alt.X('int_created_date:O', title='Month'),
        y=alt.Y('count(Total):Q', title='Transaction Count'),
        color=alt.Color('Type:N', title='Payment Type')
    ).properties(
        title={
            "text": ["Monthly Transaction Counts"],
            "subtitle": [f"Filters → Status: {PaymentStatus}, Method: {PaymentMethod}, "
                         f"App: {PaymentApplication}, Country: {PaymentCountry}, "
                         f"Dates: {StartDate.date()} to {EndDate.date()}"],
        },
        width=800,
        height=500
    )

    # ---- Tabs ----
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Histogram", "Box & Whiskers", "Monthly Totals", "Monthly Counts"]
    )
    with tab1:
        st.altair_chart(chart1, use_container_width=True)
    with tab2:
        st.altair_chart(chart2, use_container_width=True)
    with tab3:
        st.altair_chart(chart3, use_container_width=True)
    with tab4:
        st.altair_chart(chart4, use_container_width=True)