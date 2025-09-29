import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date
import plotly.express as px

# Import custom modules
from modules.data_loader import load_all_sheets_data, preprocess_portfolio_metrics, prepare_portfolio_performance_data
from modules.portfolio_metrics import (
    calculate_total_portfolio_value,
    calculate_cash_percentage,
    calculate_portfolio_beta,
    get_sp500_performance
)
from modules.utils import format_currency, format_dataframe_for_display, capitalize_column_names

# Page configuration
st.set_page_config(
    page_title="Andrei's Portfolio",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Andrei's Portfolio")

# Create connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Cached data loading wrapper
@st.cache_data(ttl="10m")
def get_portfolio_data():
    """Cached wrapper for loading and preprocessing portfolio data"""
    all_sheets_data = load_all_sheets_data(conn)
    return preprocess_portfolio_metrics(all_sheets_data)

# Cached performance data wrapper
@st.cache_data(ttl="10m")
def get_performance_data():
    """Cached wrapper for loading performance chart data"""
    all_sheets_data = load_all_sheets_data(conn)
    return prepare_portfolio_performance_data(all_sheets_data)

# Load all data and preprocess metrics
portfolio_metrics = get_portfolio_data()
available_dates = portfolio_metrics['available_dates']

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

# Initialize session state for selected date
if 'selected_date' not in st.session_state and available_dates:
    st.session_state.selected_date = available_dates[0]

# === HOMEPAGE LAYOUT ===

# 1. Portfolio Summary
st.markdown("### 📊 Portfolio Summary")
col1, col2, col3 = st.columns(3)

# Calculate actual metrics for selected date
if selected_date and selected_date in portfolio_metrics['total_values_by_date']:
    total_value = calculate_total_portfolio_value(portfolio_metrics, selected_date)
    cash_percentage = calculate_cash_percentage(portfolio_metrics, selected_date)
    beta_value = calculate_portfolio_beta(portfolio_metrics, selected_date)

    with col1:
        st.metric(
            label="Total Value",
            value=format_currency(total_value),
            delta=None
        )

    with col2:
        st.metric(
            label="Beta",
            value=f"{beta_value:.2f}",
            delta=None
        )

    with col3:
        st.metric(
            label="% in Cash",
            value=f"{cash_percentage:.1f}%",
            delta=None
        )
else:
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

# 2. Portfolio Performance Chart
st.markdown("### 📊 Portfolio Performance Over Time")

# Load performance data
performance_data = get_performance_data()

if not performance_data.empty:
    # Create stacked bar chart showing dollar allocation by group over time
    fig = px.bar(performance_data,
                x='date',
                y='balance',
                color='group',
                title='Portfolio Value by Group ($)',
                labels={'balance': 'Value ($)', 'date': 'Date'},
                hover_data={'percentage': ':.1f'},
                text='balance')

    # Update layout for better display
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value ($)",
        legend_title="Group",
        barmode='stack',
        height=400
    )

    # Format y-axis to show currency
    fig.update_yaxes(tickformat='$,.0f')

    # Format text labels inside bars to show currency
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='inside')

    # Format dates on x-axis
    fig.update_xaxes(tickformat='%b %d')

    st.plotly_chart(fig, use_container_width=True)

    # Show summary table below the chart
    if selected_date and selected_date in performance_data['date'].values:
        selected_data = performance_data[performance_data['date'] == selected_date].copy()
        if not selected_data.empty:
            selected_data = selected_data[['group', 'balance', 'percentage']].sort_values('balance', ascending=False)
            selected_data['balance'] = selected_data['balance'].apply(lambda x: f"${x:,.0f}")
            selected_data['percentage'] = selected_data['percentage'].apply(lambda x: f"{x}%")
            selected_data.columns = ['Group', 'Balance', 'Percentage']

            st.markdown(f"**Allocation for {selected_date.strftime('%B %d, %Y')}:**")
            st.dataframe(selected_data, use_container_width=True, hide_index=True)
else:
    st.info("📊 No portfolio performance data available")

st.markdown("---")

# 3. Asset Allocation Pie Charts
st.markdown("### 🥧 Asset Allocation")
if selected_date:
    asset_allocation = portfolio_metrics['asset_allocations_by_date'].get(selected_date)
    equity_allocation = portfolio_metrics['equity_allocations_by_date'].get(selected_date)

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
            display_allocation = format_dataframe_for_display(
                asset_allocation,
                currency_cols=['balance'],
                percentage_cols=[]
            )
            display_allocation['percentage'] = display_allocation['percentage'].apply(lambda x: f"{x}%")
            display_allocation.columns = ['Asset Class', 'Balance', 'Percentage']
            st.dataframe(display_allocation, use_container_width=True, hide_index=True)

        with table_col2:
            if equity_allocation is not None and not equity_allocation.empty:
                st.markdown("**Equity Class Breakdown**")
                display_equity = format_dataframe_for_display(
                    equity_allocation,
                    currency_cols=['balance'],
                    percentage_cols=[]
                )
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
    index_data = portfolio_metrics['index_performance_by_date'].get(selected_date)
    if index_data is not None and not index_data.empty:
        # Find S&P 500 data and display in simplified format
        sp500_row = index_data[index_data['index'].str.lower() == 'sp500']
        if not sp500_row.empty:
            ytd_return = sp500_row.iloc[0]['return_pct_ytd'] * 100  # Convert to percentage
            st.markdown(
                f"<small style='color: gray;'>S&P 500 (YTD Return): {ytd_return:.2f}%</small>",
                unsafe_allow_html=True
            )

if selected_date:
    portfolios_df = portfolio_metrics['portfolio_details_by_date'].get(selected_date)
    if portfolios_df is not None and not portfolios_df.empty:
        # Create display dataframe with formatting
        display_df = portfolios_df.copy()

        # Remove the date column since we're filtering by it
        if 'date' in display_df.columns:
            display_df = display_df.drop('date', axis=1)

        # Remove the balance_numeric helper column
        if 'balance_numeric' in display_df.columns:
            display_df = display_df.drop('balance_numeric', axis=1)

        # Apply centralized formatting
        display_df = format_dataframe_for_display(
            display_df,
            currency_cols=['balance'],
            percentage_cols=['return_pct_ytd'],
            beta_cols=['beta']
        )

        # Capitalize column names for display
        display_df = capitalize_column_names(display_df)

        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"📊 No portfolio data found for {selected_date.strftime('%B %d, %Y')}")
else:
    st.info("📊 Select a date to view portfolio details")