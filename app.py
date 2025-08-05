import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load data
@st.cache_data
def load_data():
    # Try to handle the comma in order numbers (like 10,107)
    data = pd.read_csv('sales_data.csv', thousands=',')
    
    # Convert ORDER_DATE to datetime
    data['ORDER_DATE'] = pd.to_datetime(data['ORDER_DATE'])
    
    # Create a YEAR-MONTH column for easier time-based analysis
    data['YEAR_MONTH'] = data['ORDER_DATE'].dt.to_period('M').astype(str)
    
    # Calculate profit margin (assuming MSRP is cost, for demonstration)
    data['PROFIT'] = data['PRICE_EACH'] - data['MSRP']
    data['PROFIT_MARGIN'] = (data['PROFIT'] / data['PRICE_EACH']) * 100
    
    return data

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
years = st.sidebar.multiselect(
    "Select Years",
    options=sorted(df['YEAR'].unique()),
    default=sorted(df['YEAR'].unique())
)

statuses = st.sidebar.multiselect(
    "Select Order Status",
    options=df['STATUS'].unique(),
    default=df['STATUS'].unique()
)

product_lines = st.sidebar.multiselect(
    "Select Product Lines",
    options=df['PRODUCTLINE'].unique(),
    default=df['PRODUCTLINE'].unique()
)

deal_sizes = st.sidebar.multiselect(
    "Select Deal Sizes",
    options=df['DEALSIZE'].unique(),
    default=df['DEALSIZE'].unique()
)

# Filter data based on selections
filtered_df = df[
    (df['YEAR'].isin(years)) &
    (df['STATUS'].isin(statuses)) &
    (df['PRODUCTLINE'].isin(product_lines)) &
    (df['DEALSIZE'].isin(deal_sizes))
]

# Main page
st.title("🚀 Sales Data Business Intelligence Dashboard")
st.markdown("Analyzing sales performance across different dimensions")

# KPI cards
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['SALES'].sum()
    st.metric("Total Sales", f"${total_sales:,.2f}")

with col2:
    avg_order_value = filtered_df['SALES'].mean()
    st.metric("Average Order Value", f"${avg_order_value:,.2f}")

with col3:
    total_orders = filtered_df['ORDER_NUMBER'].nunique()
    st.metric("Total Orders", total_orders)

with col4:
    avg_profit_margin = filtered_df['PROFIT_MARGIN'].mean()
    st.metric("Avg Profit Margin", f"{avg_profit_margin:.1f}%")

# Sales Trends
st.subheader("Sales Trends Over Time")
sales_trend = filtered_df.groupby('YEAR_MONTH')['SALES'].sum().reset_index()
fig1 = px.line(
    sales_trend, 
    x='YEAR_MONTH', 
    y='SALES',
    title="Monthly Sales Trend",
    labels={'SALES': 'Total Sales ($)', 'YEAR_MONTH': 'Month'}
)
st.plotly_chart(fig1, use_container_width=True)

# Sales by Product Line
st.subheader("Sales by Product Line")
sales_by_product = filtered_df.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
fig2 = px.bar(
    sales_by_product,
    x='PRODUCTLINE',
    y='SALES',
    title="Total Sales by Product Line",
    labels={'SALES': 'Total Sales ($)', 'PRODUCTLINE': 'Product Line'}
)
st.plotly_chart(fig2, use_container_width=True)

# Sales by Country
st.subheader("Sales by Country")
sales_by_country = filtered_df.groupby('COUNTRY')['SALES'].sum().reset_index()
fig3 = px.choropleth(
    sales_by_country,
    locations='COUNTRY',
    locationmode='country names',
    color='SALES',
    title="Sales by Country",
    hover_name='COUNTRY',
    color_continuous_scale=px.colors.sequential.Plasma
)
st.plotly_chart(fig3, use_container_width=True)

# Deal Size Distribution
st.subheader("Deal Size Distribution")
deal_size_dist = filtered_df['DEALSIZE'].value_counts().reset_index()
fig4 = px.pie(
    deal_size_dist,
    names='DEALSIZE',
    values='count',
    title="Deal Size Distribution"
)
st.plotly_chart(fig4, use_container_width=True)

# Top Customers
st.subheader("Top 10 Customers by Sales")
top_customers = filtered_df.groupby('CUSTOMER_NAME')['SALES'].sum().nlargest(10).reset_index()
fig5 = px.bar(
    top_customers,
    x='SALES',
    y='CUSTOMER_NAME',
    orientation='h',
    title="Top Customers by Sales",
    labels={'SALES': 'Total Sales ($)', 'CUSTOMER_NAME': 'Customer'}
)
st.plotly_chart(fig5, use_container_width=True)

# Profit Analysis
st.subheader("Profit Analysis")
fig6 = px.scatter(
    filtered_df,
    x='QUANTITY_ORDERED',
    y='PROFIT',
    color='PRODUCTLINE',
    size='SALES',
    hover_data=['PRODUCTCODE', 'PRICE_EACH', 'MSRP'],
    title="Profit vs. Quantity Ordered"
)
st.plotly_chart(fig6, use_container_width=True)

# Raw Data
st.subheader("Raw Data")
st.dataframe(filtered_df)

# Download filtered data
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_sales_data.csv',
    mime='text/csv'
)
