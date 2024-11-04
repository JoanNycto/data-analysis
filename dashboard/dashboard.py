import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Load your dataset
all_data = pd.read_csv("all_data.csv")

# Convert date columns if necessary
all_data['order_purchase_timestamp'] = pd.to_datetime(all_data['order_purchase_timestamp'])
all_data['order_delivered_customer_date'] = pd.to_datetime(all_data['order_delivered_customer_date'])

# Function to create daily metrics
def create_daily_metrics_df(orders_df):
    daily_df = orders_df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id': 'nunique',  # Unique orders
        'order_status': 'count'  # Total orders
    }).reset_index()
    daily_df.rename(columns={'order_id': 'order_count', 'order_status': 'total_orders'}, inplace=True)
    return daily_df

# Create DataFrame for daily metrics
daily_metrics_df = create_daily_metrics_df(all_data)

# Streamlit sidebar for date input
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Date Range',
        value=(daily_metrics_df['order_purchase_timestamp'].min().date(), 
            daily_metrics_df['order_purchase_timestamp'].max().date())
    )

# Convert date inputs to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data based on date input
main_df = daily_metrics_df[(daily_metrics_df['order_purchase_timestamp'] >= start_date) & 
                            (daily_metrics_df['order_purchase_timestamp'] <= end_date)]

# Streamlit header
st.header('E-commerce Dashboard')

# Display total orders
total_orders = main_df['order_count'].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Orders", value=total_orders)

# Daily orders line chart
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(main_df['order_purchase_timestamp'], main_df['order_count'], marker='o', linewidth=2, color="#90CAF9")
ax.set_title('Daily Orders', fontsize=20)
ax.set_xlabel('Date', fontsize=14)
ax.set_ylabel('Order Count', fontsize=14)
st.pyplot(fig)

# Additional visualizations: Order payments
# Grouping by payment type
payment_summary = all_data.groupby('payment_type')['payment_value'].sum().reset_index()
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(x='payment_type', y='payment_value', data=payment_summary, palette='viridis', ax=ax2)
ax2.set_title('Total Payments by Type', fontsize=20)
ax2.set_xlabel('Payment Type', fontsize=14)
ax2.set_ylabel('Total Payment Value', fontsize=14)
st.pyplot(fig2)

# 1. Order Status Distribution
status_summary = all_data['order_status'].value_counts().reset_index()
status_summary.columns = ['Order Status', 'Count']
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.barplot(x='Order Status', y='Count', data=status_summary, palette='magma', ax=ax3)
ax3.set_title('Order Status Distribution', fontsize=20)
ax3.set_xlabel('Status', fontsize=14)
ax3.set_ylabel('Number of Orders', fontsize=14)
st.pyplot(fig3)

# 2. Best-Selling Products
best_selling_products = all_data.groupby('product_id')['order_id'].count().reset_index()
best_selling_products.columns = ['Product ID', 'Sales Count']
best_selling_products = best_selling_products.sort_values(by='Sales Count', ascending=False).head(10)
fig4, ax4 = plt.subplots(figsize=(10, 6))
sns.barplot(x='Sales Count', y='Product ID', data=best_selling_products, palette='Blues', ax=ax4)
ax4.set_title('Top 10 Best-Selling Products', fontsize=20)
ax4.set_xlabel('Number of Sales', fontsize=14)
ax4.set_ylabel('Product ID', fontsize=14)
st.pyplot(fig4)

# 3. Customer Demographics - Zip Code Distribution
zip_code_summary = all_data['customer_zip_code_prefix'].value_counts().reset_index()
zip_code_summary.columns = ['Zip Code', 'Count']
fig5, ax5 = plt.subplots(figsize=(10, 6))
sns.barplot(x='Zip Code', y='Count', data=zip_code_summary.head(10), palette='coolwarm', ax=ax5)
ax5.set_title('Top 10 Zip Codes by Number of Customers', fontsize=20)
ax5.set_xlabel('Zip Code', fontsize=14)
ax5.set_ylabel('Number of Customers', fontsize=14)
st.pyplot(fig5)

# Caption or footer
st.caption('Copyright (c) Allycia Joan Micheline 2024')
