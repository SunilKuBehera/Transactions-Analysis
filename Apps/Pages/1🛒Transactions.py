import streamlit as st
import pandas as pd
import numpy as np
import io
import xlsxwriter
from datetime import date, timedelta

st.set_page_config(page_title="Transactions", page_icon="🛒")

st.title("Transaction Breakdown")

filename = st.text_input("Filename", key="filename")
firstname = st.text_input("Enter Name", key="firstname1")
highticketval = st.number_input("Enter High Ticket (INTEGER ONLY)", key="highticket")

uploaded_file = st.file_uploader("Please Upload CSV File", type=['csv'])

if uploaded_file is not None:

    dfpreclean = pd.read_csv(uploaded_file)

    # Drop unnecessary columns
    dfpreclean.drop(['Transaction_ID', 'Auth_code'], axis=1, inplace=True, errors='ignore')
    dfpreclean = dfpreclean[dfpreclean['Success'] == 1]
    dfpreclean["Transaction_Notes"].fillna("N/A", inplace=True)
    dfpreclean['Day'] = pd.to_datetime(dfpreclean['Day'])

    df = dfpreclean.loc[:, [
        'Total', 'Transaction_Type', 'Type', 'Country',
        'Source', 'Day', 'Customer_Name', 'Transaction_Notes'
    ]]

    # ---- Basic calculations ----
    total_sum = df['Total'].sum()
    total_transactions = df['Type'].count()
    mean_transaction = df['Total'].mean()
    median_transaction = df['Total'].median()
    mode_transaction = df['Total'].mode().iloc[0] if not df['Total'].mode().empty else np.nan
    max_transaction = df['Total'].max()

    # Transaction type subsets
    charge_df = df[df['Type'] == 'Charge']
    refund_df = df[df['Type'] == 'Refund']
    chargeback_df = df[df['Type'] == 'Chargeback']

    days90 = pd.to_datetime(date.today() - timedelta(days=90))
    days180 = pd.to_datetime(date.today() - timedelta(days=180))

    # Charges
    charge_total = charge_df['Total'].sum()
    charge_90days = charge_df.loc[charge_df['Day'] > days90, 'Total'].sum()
    charge_180days = charge_df.loc[charge_df['Day'] > days180, 'Total'].sum()

    # Refunds
    refund_total = refund_df['Total'].sum()
    refund_90days = refund_df.loc[refund_df['Day'] > days90, 'Total'].sum()
    refund_180days = refund_df.loc[refund_df['Day'] > days180, 'Total'].sum()

    # Chargebacks
    chargeBack_total = chargeback_df['Total'].sum()
    chargeBack_90days = chargeback_df.loc[chargeback_df['Day'] > days90, 'Total'].sum()
    chargeBack_180days = chargeback_df.loc[chargeback_df['Day'] > days180, 'Total'].sum()

    # Safe division
    def safe_divide(a, b):
        return a / b if b != 0 else 0

    refundRate_lifetime = safe_divide(refund_total, charge_total)
    refundRate_90days = safe_divide(refund_90days, charge_90days)
    refundRate_180days = safe_divide(refund_180days, charge_180days)

    chargeBackRate_lifetime = safe_divide(chargeBack_total, charge_total)
    chargeBackRate_90days = safe_divide(chargeBack_90days, charge_90days)
    chargeBackRate_180days = safe_divide(chargeBack_180days, charge_180days)

    # ---- Customer analysis ----
    pivottablenames = pd.pivot_table(
        df,
        index=['Customer_Name'],
        aggfunc={'Total': np.sum, 'Customer_Name': 'count'}
    )
    pivottablenames = pivottablenames.rename(
        columns={"Customer_Name": "count_of_total", "Total": "sum_of_total"}
    )
    total_unique_customers = pivottablenames.shape[0]
    avg_transaction_count_per_customer = pivottablenames['count_of_total'].mean()
    avg_transaction_sum_per_customer = pivottablenames['sum_of_total'].mean()

    # Transaction type pivot
    pivottabltransactiontype = pd.pivot_table(
        df,
        index=['Transaction_Type'],
        aggfunc={'Transaction_Type': 'count', 'Total': np.sum}
    )
    pivottabltransactiontype['totalpercent'] = (
        pivottabltransactiontype['Total'] / total_sum
    ).apply('{:.2%}'.format)

    # Country pivot
    pivottabltransactioncountry = pd.pivot_table(
        df,
        index=['Country'],
        aggfunc={'Country': 'count', 'Total': np.sum}
    )
    pivottabltransactioncountry['totalpercent'] = (
        pivottabltransactioncountry['Total'] / total_sum
    ).apply('{:.2%}'.format)

    # Name check
    namefinal = df[df['Customer_Name'].str.contains(firstname, case=False, na=False)]

    # Flagged payment notes
    flagged_words = 'raffle|giveaway|prize|razz|lottery'
    payment_note_final = df[df['Transaction_Notes'].str.contains(flagged_words, case=False, na=False)]

    # High-ticket transactions
    highticket_df = df[df['Total'] >= highticketval].sort_values(by='Total', ascending=False)

    # Duplicate same-day transactions by same customer
    dup = df.copy()
    dup['Customer_Name_prev'] = dup['Customer_Name'].shift(-1)
    dup['Customer_Name_next'] = dup['Customer_Name'].shift(1)
    dup['Created_at_day_prev'] = dup['Day'].shift(-1)
    dup['Created_at_day_next'] = dup['Day'].shift(1)
    dup3 = dup.query(
        '(Day == Created_at_day_prev | Day == Created_at_day_next) & '
        '(Customer_Name == Customer_Name_next | Customer_Name == Customer_Name_prev)'
    )

    # ---- Summary DF ----
    df_cal = pd.DataFrame({
        'total_sum': [total_sum],
        'mean_transaction': [mean_transaction],
        'median_transaction': [median_transaction],
        'mode_transaction': [mode_transaction],
        'max_transaction': [max_transaction],
        'total_transactions': [total_transactions],
        'charge_total': [charge_total],
        'charge_90days': [charge_90days],
        'charge_180days': [charge_180days],
        'refund_total': [refund_total],
        'refund_90days': [refund_90days],
        'refund_180days': [refund_180days],
        'refundRate_lifetime': [refundRate_lifetime],
        'refundRate_90days': [refundRate_90days],
        'refundRate_180days': [refundRate_180days],
        'chargeBack_total': [chargeBack_total],
        'chargeBack_90days': [chargeBack_90days],
        'chargeBack_180days': [chargeBack_180days],
        'chargeBackRate_lifetime': [chargeBackRate_lifetime],
        'chargeBackRate_90days': [chargeBackRate_90days],
        'chargeBackRate_180days': [chargeBackRate_180days],
        'total_unique_customers': [total_unique_customers],
        'avg_transaction_count_per_customer': [avg_transaction_count_per_customer],
        'avg_transaction_sum_per_customer': [avg_transaction_sum_per_customer],
        '90_days': [days90],
        '180_days': [days180]
    })

    # ---- Excel Export ----
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Clean_Data')
        df_cal.to_excel(writer, sheet_name='Calculations')
        pivottablenames.to_excel(writer, sheet_name='Names')
        pivottabltransactiontype.to_excel(writer, sheet_name='Transaction_Type')
        pivottabltransactioncountry.to_excel(writer, sheet_name='Country')
        payment_note_final.to_excel(writer, sheet_name='Payment_Notes')
        highticket_df.to_excel(writer, sheet_name='High_Ticket')
        namefinal.to_excel(writer, sheet_name='Name_Checker')
        dup3.to_excel(writer, sheet_name='Double_Transactions')

    st.download_button(
        label="Download Excel worksheets",
        data=buffer,
        file_name=f"{st.session_state.filename}.xlsx",
        mime="application/vnd.ms-excel"
    )

else:
    st.warning("You need to upload a CSV file.")