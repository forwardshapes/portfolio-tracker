import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Andrei's Portfolio",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Andrei's Portfolio")

# Create connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_available_dates():
    """Load available dates from the portfolios tab"""
    try:
        df = conn.read(ttl="10m", worksheet="portfolios")
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            # Get unique dates and sort them in descending order (most recent first)
            dates = sorted(df['date'].dropna().unique(), reverse=True)
            return dates
    except:
        pass
    return []

def load_portfolios_data(selected_date):
    """Load portfolios data filtered by selected date"""
    try:
        df = conn.read(ttl="10m", worksheet="portfolios")
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            # Filter by selected date
            filtered_df = df[df['date'] == selected_date].copy()
            if not filtered_df.empty:
                return filtered_df
    except:
        pass
    return None

def load_assets_data(selected_date):
    """Load assets data filtered by selected date and aggregate by asset_class"""
    try:
        df = conn.read(ttl="10m", worksheet="assets")
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            # Filter by selected date
            filtered_df = df[df['date'] == selected_date].copy()
            if not filtered_df.empty:
                # Convert balance to numeric
                filtered_df['balance'] = pd.to_numeric(filtered_df['balance'], errors='coerce').fillna(0)
                # Aggregate by asset_class
                asset_allocation = filtered_df.groupby('asset_class')['balance'].sum().reset_index()
                # Calculate percentages
                total_balance = asset_allocation['balance'].sum()
                if total_balance > 0:
                    asset_allocation['percentage'] = (asset_allocation['balance'] / total_balance * 100).round(1)
                    return asset_allocation
    except:
        pass
    return None

def load_equity_allocation_data(selected_date):
    """Load equity assets data filtered by selected date and aggregate by equity_class"""
    try:
        df = conn.read(ttl="10m", worksheet="assets")
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            # Filter by selected date
            filtered_df = df[df['date'] == selected_date].copy()
            if not filtered_df.empty:
                # Filter for equity assets only
                equity_df = filtered_df[filtered_df['asset_class'].str.lower() == 'equity'].copy()
                if not equity_df.empty:
                    # Convert balance to numeric
                    equity_df['balance'] = pd.to_numeric(equity_df['balance'], errors='coerce').fillna(0)
                    # Aggregate by equity_class
                    equity_allocation = equity_df.groupby('equity_class')['balance'].sum().reset_index()
                    # Calculate percentages
                    total_balance = equity_allocation['balance'].sum()
                    if total_balance > 0:
                        equity_allocation['percentage'] = (equity_allocation['balance'] / total_balance * 100).round(1)
                        return equity_allocation
    except:
        pass
    return None

def load_index_performance(selected_date):
    """Load index performance data for selected date"""
    try:
        df = conn.read(ttl="10m", worksheet="indexes")
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            # Filter by selected date
            filtered_df = df[df['date'] == selected_date].copy()
            if not filtered_df.empty:
                # Convert return_pct_ytd to numeric and format as percentage
                filtered_df['return_pct_ytd'] = pd.to_numeric(filtered_df['return_pct_ytd'], errors='coerce')
                return filtered_df
    except:
        pass
    return None

# Load available dates
available_dates = load_available_dates()

# Date selector
if available_dates:
    selected_date = st.selectbox(
        "📅 Select Date:",
        options=available_dates,
        format_func=lambda x: x.strftime('%B %d, %Y'),
        index=0  # Default to most recent date
    )
else:
    selected_date = None
    st.caption("📅 No dates available from portfolios sheet")

# === HOMEPAGE LAYOUT ===

# 1. Portfolio Summary
st.markdown("### 📊 Portfolio Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Value",
        value="--",
        delta=None
    )

with col2:
    st.metric(
        label="Beta",
        value="--",
        delta=None
    )

with col3:
    st.metric(
        label="% in Cash",
        value="--",
        delta=None
    )

st.markdown("---")

# 2. Monthly Performance Chart
st.markdown("### 📊 Portfolio Performance (2025)")
if selected_date:
    st.info(f"📊 Performance chart for {selected_date.strftime('%B %d, %Y')} will be displayed here once data is loaded")
else:
    st.info("📊 Select a date to view performance chart")

st.markdown("---")

# 3. Asset Allocation Pie Charts
st.markdown("### 🥧 Asset Allocation")
if selected_date:
    asset_allocation = load_assets_data(selected_date)
    equity_allocation = load_equity_allocation_data(selected_date)

    # Create two columns for side-by-side charts
    chart_col1, chart_col2 = st.columns(2)

    # By Class chart (left side)
    with chart_col1:
        if asset_allocation is not None and not asset_allocation.empty:
            fig_class = px.pie(asset_allocation,
                        values='balance',
                        names='asset_class',
                        title='By Class',
                        hover_data=['percentage'])
            fig_class.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_class, use_container_width=True)
        else:
            st.info("📊 No asset class data available")

    # By Equity chart (right side)
    with chart_col2:
        if equity_allocation is not None and not equity_allocation.empty:
            fig_equity = px.pie(equity_allocation,
                        values='balance',
                        names='equity_class',
                        title='By Equity',
                        hover_data=['percentage'])
            fig_equity.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_equity, use_container_width=True)
        else:
            st.info("📊 No equity data available")

    # Show allocation tables below charts
    if asset_allocation is not None and not asset_allocation.empty:
        table_col1, table_col2 = st.columns(2)

        with table_col1:
            st.markdown("**Asset Class Breakdown**")
            display_allocation = asset_allocation.copy()
            display_allocation['balance'] = display_allocation['balance'].apply(lambda x: f"${x:,.0f}")
            display_allocation['percentage'] = display_allocation['percentage'].apply(lambda x: f"{x}%")
            display_allocation.columns = ['Asset Class', 'Balance', 'Percentage']
            st.dataframe(display_allocation, use_container_width=True, hide_index=True)

        with table_col2:
            if equity_allocation is not None and not equity_allocation.empty:
                st.markdown("**Equity Class Breakdown**")
                display_equity = equity_allocation.copy()
                display_equity['balance'] = display_equity['balance'].apply(lambda x: f"${x:,.0f}")
                display_equity['percentage'] = display_equity['percentage'].apply(lambda x: f"{x}%")
                display_equity.columns = ['Equity Class', 'Balance', 'Percentage']
                st.dataframe(display_equity, use_container_width=True, hide_index=True)
            else:
                st.info("📊 No equity breakdown available")
else:
    st.info("📊 Select a date to view asset allocation")

st.markdown("---")

# 4. Portfolio Details Table
st.markdown("### 📋 Portfolio Details")

# Index performance section (above table)
if selected_date:
    index_data = load_index_performance(selected_date)
    if index_data is not None and not index_data.empty:
        # Find S&P 500 data and display in simplified format
        sp500_row = index_data[index_data['index'].str.lower() == 'sp500']
        if not sp500_row.empty:
            ytd_return = sp500_row.iloc[0]['return_pct_ytd'] * 100  # Convert to percentage
            st.markdown(
                f"<small style='color: gray;'>S&P 500 (YTD): {ytd_return:.2f}%</small>",
                unsafe_allow_html=True
            )

if selected_date:
    portfolios_df = load_portfolios_data(selected_date)
    if portfolios_df is not None and not portfolios_df.empty:
        # Create display dataframe with formatting
        display_df = portfolios_df.copy()

        # Remove the date column since we're filtering by it
        if 'date' in display_df.columns:
            display_df = display_df.drop('date', axis=1)

        # Format balance as currency
        if 'balance' in display_df.columns:
            display_df['balance'] = pd.to_numeric(display_df['balance'], errors='coerce')
            display_df['balance'] = display_df['balance'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "--")

        # Format return_pct_ytd as percentage (multiply by 100 since source data is in decimal format)
        if 'return_pct_ytd' in display_df.columns:
            display_df['return_pct_ytd'] = pd.to_numeric(display_df['return_pct_ytd'], errors='coerce')
            display_df['return_pct_ytd'] = display_df['return_pct_ytd'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "--")

        # Capitalize column names for display
        display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]

        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"📊 No portfolio data found for {selected_date.strftime('%B %d, %Y')}")
else:
    st.info("📊 Select a date to view portfolio details")