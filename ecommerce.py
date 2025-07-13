import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config and custom CSS
st.set_page_config(page_title="E-commerce Analytics Dashboard", layout="wide", page_icon="🛒")

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_ecommerce_data():
    try:
        df = pd.read_csv('ecommerce.csv')
        return df
    except FileNotFoundError:
        st.error("Please make sure 'ecommerce.csv' file is in the same directory as this script.")
        return None

def apply_filters(df):
    st.sidebar.header("🔧 Filter Options")
    
    months = ['All'] + sorted(df['order_month'].unique().tolist()) if 'order_month' in df.columns else ['All']
    selected_months = st.sidebar.multiselect("📅 Select Months:", options=months, default=['All'])

    categories = ['All'] + sorted(df['product_category_name_english'].unique().tolist(), reverse=True) if 'product_category_name_english' in df.columns else ['All']
    selected_category = st.sidebar.multiselect("🛍️ Select Product Category:", options=categories, default=['All'])

    states = ['All'] + sorted(df['customer_state'].unique().tolist(), reverse=True) if 'customer_state' in df.columns else ['All']
    selected_states = st.sidebar.multiselect("🏢 Select States:", options=states, default=['All'])

    if 'review_score' in df.columns:
        min_review, max_review = st.sidebar.slider("⭐ Review Score Range:", int(df['review_score'].min()), int(df['review_score'].max()), (int(df['review_score'].min()), int(df['review_score'].max())))
    else:
        min_review, max_review = 1, 5

    payments = ['All'] + sorted(df['payment_type'].unique().tolist()) if 'payment_type' in df.columns else ['All']
    selected_payment = st.sidebar.selectbox("💳 Payment Type:", payments)

    filtered_df = df.copy()

    if 'order_month' in df.columns and 'All' not in selected_months:
        filtered_df = filtered_df[filtered_df['order_month'].isin(selected_months)]

    if 'product_category_name_english' in df.columns and 'All' not in selected_category:
        filtered_df = filtered_df[filtered_df['product_category_name_english'].isin(selected_category)]

    if 'customer_state' in df.columns and 'All' not in selected_states:
        filtered_df = filtered_df[filtered_df['customer_state'].isin(selected_states)]

    if 'review_score' in df.columns:
        filtered_df = filtered_df[(filtered_df['review_score'] >= min_review) & (filtered_df['review_score'] <= max_review)]

    if 'payment_type' in df.columns and selected_payment != 'All':
        filtered_df = filtered_df[filtered_df['payment_type'] == selected_payment]

    return filtered_df

def calculate_kpis(df):
    if len(df) == 0:
        return dict.fromkeys(['total_orders', 'total_revenue', 'avg_rating', 'avg_freight_cost', 'total_customers', 'avg_price'], 0)
    
    return {
        'total_orders': len(df),
        'total_revenue': df['total_order_value'].sum() if 'total_order_value' in df.columns else 0,
        'avg_rating': df['review_score'].mean() if 'review_score' in df.columns else 0,
        'avg_freight_cost': df['freight_value'].mean() if 'freight_value' in df.columns else 0,
        'total_customers': df['customer_unique_id'].nunique() if 'customer_unique_id' in df.columns else 0,
        'avg_price': df['price'].mean() if 'price' in df.columns else 0
    }

def display_kpis(kpis):
    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    
    with col1:
        st.metric("📦 Total Orders", f"{kpis['total_orders']:,}")
    with col2:
        st.metric("💰 Total Revenue", f"${kpis['total_revenue']:,.2f}")
    with col3:
        st.metric("💵 Avg Price", f"${kpis['avg_price']:,.2f}")
    with col4:
        st.metric("⭐ Avg Rating", f"{kpis['avg_rating']:.2f}/5")
    with col5:
        st.metric("👥 Total Customers", f"{kpis['total_customers']:,}")
    with col6:
        st.metric("📦 Avg Freight Cost", f"${kpis['avg_freight_cost']:,.2f}")

def create_visualizations(df):
    st.markdown("---")
    st.markdown("### 📊 Data Visualizations")

    st.markdown("#### 📈 Sales Analytics")
    col1, col2 = st.columns(2)
    with col1:
        if 'order_month' in df.columns and 'total_order_value' in df.columns:
            sales = df.groupby('order_month')['total_order_value'].sum().reset_index()
            fig = px.line(sales, x='order_month', y='total_order_value', title='Total Monthly Sales Over Time', markers=True)
            fig.update_layout(xaxis_title="Month", yaxis_title="Total Sales ($)", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if 'customer_state' in df.columns and 'total_order_value' in df.columns:
            state_sales = df.groupby('customer_state')['total_order_value'].sum().sort_values(ascending=True).head(10)
            fig = px.bar(x=state_sales.values, y=state_sales.index, orientation='h', title='Top 10 States by Sales', labels={'x': 'Total Sales ($)', 'y': 'State'}, color=state_sales.values, color_continuous_scale='Blues')
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 🛍️ Product Analytics")
    col3, col4 = st.columns(2)
    with col3:
        if 'product_category_name_english' in df.columns:
            top = df['product_category_name_english'].value_counts().head(10).sort_values(ascending=True)
            fig = px.bar(x=top.values, y=top.index, orientation='h', title='Top 10 Product Categories by Count', labels={'x': 'Count', 'y': 'Product Category'}, color=top.values, color_continuous_scale='darkmint')
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
    with col4:
        if 'price' in df.columns:
            fig = px.histogram(df, x='price', nbins=30, title='Distribution of Product Prices', labels={'price': 'Price ($)'})
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    if 'price' in df.columns and 'freight_value' in df.columns:
        fig = px.scatter(df, x="price", y="freight_value", title="Freight Cost vs Product Price", labels={'price': 'Price ($)', 'freight_value': 'Freight Value ($)'}, color='price', color_continuous_scale='Cividis')
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 🚚 Delivery Analytics")
    col5, col6 = st.columns(2)
    with col5:
        if 'review_score' in df.columns and 'delivery_days' in df.columns:
            fig = px.box(df, x='review_score', y='delivery_days', title='Delivery Time by Review Score', labels={'review_score': 'Review Score', 'delivery_days': 'Delivery Time (Days)'}, color='review_score')
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
    with col6:
        if 'customer_state' in df.columns and 'delivery_days' in df.columns:
            avg = df.groupby('customer_state')['delivery_days'].mean().sort_values().head(10).sort_values(ascending=True)
            fig = px.bar(x=avg.index, y=avg.values, title='Top 10 States by Avg Delivery Time', labels={'x': 'State', 'y': 'Avg Delivery Time (Days)'}, color=avg.values, color_continuous_scale='Blues')
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    if 'estimated_days' in df.columns and 'delivery_delay' in df.columns:
        fig = px.scatter(df, x='estimated_days', y='delivery_delay', title='Delivery Delay vs. Estimated Delivery Time', labels={'estimated_days': 'Estimated Delivery Time (days)', 'delivery_delay': 'Delivery Delay (days)'}, opacity=0.6, trendline='ols', color='delivery_delay', color_continuous_scale='YlOrRd')
        fig.update_traces(marker=dict(size=6, color='royalblue'))
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 💳 Payment Analytics")
    col7, col8 = st.columns(2)
    with col7:
        if 'payment_type' in df.columns:
            counts = df['payment_type'].value_counts()
            fig = px.pie(values=counts.values, names=counts.index, title='Payment Method Distribution', color=counts.values)
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
    with col8:
        if 'payment_type' in df.columns and 'review_score' in df.columns:
            avg = df.groupby('payment_type')['review_score'].mean().sort_values(ascending=True)
            fig = px.bar(x=avg.index, y=avg.values, title='Avg Review Score by Payment Type', labels={'x': 'Payment Type', 'y': 'Avg Review Score'}, color=avg.values)
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

def main():
    st.markdown("""
    <div class="main-header">
        <h1>🛒 E-commerce Analytics Dashboard</h1>
        <p>Welcome to the interactive E-commerce Dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_ecommerce_data()

    if df is not None:
        filtered_df = apply_filters(df)
        st.success(f"📋 Showing {len(filtered_df):,} orders out of {len(df):,} total orders")

        kpis = calculate_kpis(filtered_df)
        display_kpis(kpis)

        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if len(filtered_df) > 0:
                st.download_button("📥 Download Filtered Data", filtered_df.to_csv(index=False).encode('utf-8'), file_name=f'ecommerce_data_filtered_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv')
        with col2:
            st.download_button("📥 Download Full Dataset", df.to_csv(index=False).encode('utf-8'), file_name=f'ecommerce_data_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv')

        if st.sidebar.checkbox("Show Raw Data"):
            st.markdown("### 📄 Raw Data Preview")
            if len(filtered_df) > 0:
                st.dataframe(filtered_df, use_container_width=True, height=300)
            else:
                st.info("No data to display with current filters")

        if len(filtered_df) > 0:
            create_visualizations(filtered_df)
        else:
            st.warning("⚠️ No data available with current filters.")

        st.markdown("---")
        st.markdown("### 📊 Dataset Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Total Records:** {len(filtered_df):,}")
        with col2:
            st.info(f"**Total Columns:** {len(filtered_df.columns)}")
        with col3:
            st.info(f"**Memory Usage:** {filtered_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        st.markdown("---")
        st.markdown("""<div style="text-align: center; color: #666; margin-top: 2rem;">
            <p>E-commerce Analytics Dashboard v1.0</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.error("Unable to load the dataset. Please check if 'ecommerce.csv' exists in the current directory.")

if __name__ == "__main__":
    main()