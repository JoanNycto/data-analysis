import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
import streamlit as st

# Directory containing the CSV
data_dir = "../data/"

# Load datasets
geolocation = pd.read_csv(data_dir + 'geolocation_dataset.csv')
items = pd.read_csv(data_dir + 'order_items_dataset.csv')
reviews = pd.read_csv(data_dir + 'order_reviews_dataset.csv')
payments = pd.read_csv(data_dir + 'order_payments_dataset.csv')
orders = pd.read_csv(data_dir + 'orders_dataset.csv')
products = pd.read_csv(data_dir + 'products_dataset.csv')
customers = pd.read_csv(data_dir + 'customers_dataset.csv')
sellers = pd.read_csv(data_dir + 'sellers_dataset.csv')
category = pd.read_csv(data_dir + 'product_category_name_translation.csv')

# Data cleaning
orders_cleaned = orders.dropna(subset=['order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date'])
products_cleaned = products.dropna(subset=['product_category_name', 'product_name_lenght', 'product_description_lenght'])
orders_cleaned['order_purchase_timestamp'] = pd.to_datetime(orders_cleaned['order_purchase_timestamp'])
orders_cleaned['order_approved_at'] = pd.to_datetime(orders_cleaned['order_approved_at'])
orders_cleaned['order_delivered_carrier_date'] = pd.to_datetime(orders_cleaned['order_delivered_carrier_date'])
orders_cleaned['order_delivered_customer_date'] = pd.to_datetime(orders_cleaned['order_delivered_customer_date'])
orders_cleaned['order_estimated_delivery_date'] = pd.to_datetime(orders_cleaned['order_estimated_delivery_date'])
products_cleaned = products_cleaned.dropna(subset=['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'])

# Merge datasets for analysis
full_data = orders.merge(customers, on='customer_id', how='inner')\
                .merge(items, on='order_id', how='inner')\
                .merge(products, on='product_id', how='inner')\
                .merge(sellers, on='seller_id', how='inner')\
                .merge(category, on='product_category_name', how='left')\
                .merge(payments, on='order_id', how='inner')\
                .merge(reviews, on='order_id', how='inner')

# RFM Analysis
rfm = full_data.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (pd.to_datetime('today') - x.max()).days,
    'order_id': 'count',
    'payment_value': 'sum'
}).rename(columns={
    'order_purchase_timestamp': 'Recency',
    'order_id': 'Frequency',
    'payment_value': 'Monetary'
})

# Assign RFM scores
rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=False, duplicates='drop') + 1
rfm['F_Score'] = pd.qcut(rfm['Frequency'], 5, labels=False, duplicates='drop') + 1
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=False, duplicates='drop') + 1
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

# Segment customers
def rfm_segment(row):
    if row['RFM_Score'] in ['11', '12', '13', '21', '22', '23']:
        return 'High Value'
    elif row['RFM_Score'] in ['31', '32', '33', '41', '42', '43']:
        return 'Medium Value'
    else:
        return 'Low Value'

rfm['Segment'] = rfm.apply(rfm_segment, axis=1)

# Streamlit Visualizations
st.title("Customer RFM Analysis Dashboard")

# Display RFM Data
if st.checkbox("Show RFM Data"):
    st.dataframe(rfm.head())

# 1. Distribution of Recency
st.subheader("Distribution of Recency")
fig1, ax1 = plt.subplots()
sns.histplot(rfm['Recency'], bins=30, kde=True, ax=ax1)
ax1.set_title('Distribution of Recency')
ax1.set_xlabel('Recency (Days since last purchase)')
ax1.set_ylabel('Frequency')
st.pyplot(fig1)

# 2. Distribution of Frequency
st.subheader("Distribution of Frequency")
fig2, ax2 = plt.subplots()
sns.histplot(rfm['Frequency'], bins=30, kde=True, ax=ax2)
ax2.set_title('Distribution of Frequency')
ax2.set_xlabel('Frequency (Number of Purchases)')
ax2.set_ylabel('Frequency')
st.pyplot(fig2)

# 3. Distribution of Monetary Value
st.subheader("Distribution of Monetary Value")
fig3, ax3 = plt.subplots()
sns.histplot(rfm['Monetary'], bins=30, kde=True, ax=ax3)
ax3.set_title('Distribution of Monetary Value')
ax3.set_xlabel('Monetary Value (Total Spend)')
ax3.set_ylabel('Frequency')
st.pyplot(fig3)

# 4. RFM Score Distribution
st.subheader("RFM Score Distribution")
fig4, ax4 = plt.subplots()
sns.countplot(data=rfm, x='RFM_Score', ax=ax4, palette='viridis')
ax4.set_title('RFM Score Distribution')
ax4.set_xlabel('RFM Score')
ax4.set_ylabel('Number of Customers')
plt.xticks(rotation=45)
st.pyplot(fig4)

# 5. Customer Segmentation
st.subheader("Customer Segmentation")
fig5, ax5 = plt.subplots()
sns.countplot(data=rfm, x='Segment', ax=ax5, palette='Set2')
ax5.set_title('Customer Segmentation')
ax5.set_xlabel('Segment')
ax5.set_ylabel('Number of Customers')
st.pyplot(fig5)

# 6. Heatmap of RFM Scores
st.subheader("Heatmap of RFM Scores")
fig6, ax6 = plt.subplots(figsize=(8, 6))
rfm_heatmap_data = rfm.groupby(['R_Score', 'F_Score', 'M_Score']).size().unstack(fill_value=0)
sns.heatmap(rfm_heatmap_data, annot=True, fmt='d', cmap='YlGnBu', ax=ax6)
ax6.set_title('Heatmap of RFM Scores')
ax6.set_xlabel('F Score')
ax6.set_ylabel('R Score')
st.pyplot(fig6)

# Optional: Further analysis and plots can be added here

# Sidebar for additional options or filters can be included as needed
