"""
Data loading and preprocessing functions for the portfolio tracker.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from streamlit_gsheets import GSheetsConnection
from .portfolio_metrics import calculate_portfolio_level_beta


def load_all_sheets_data(conn: GSheetsConnection) -> Dict[str, pd.DataFrame]:
    """Load all sheets data in a single cached operation to minimize API calls"""
    try:
        data = {
            'portfolios': conn.read(worksheet="portfolios"),
            'assets': conn.read(worksheet="assets"),
            'indexes': conn.read(worksheet="indexes")
        }

        # Convert date columns to datetime for all sheets
        for sheet_name, df in data.items():
            if not df.empty and 'date' in df.columns:
                data[sheet_name]['date'] = pd.to_datetime(df['date'])

        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return {'portfolios': pd.DataFrame(), 'assets': pd.DataFrame(), 'indexes': pd.DataFrame()}


@st.cache_data(ttl="10m")
def preprocess_portfolio_metrics(all_data: Dict[str, pd.DataFrame]) -> Dict[str, any]:
    """Preprocess and calculate portfolio metrics once to avoid repeated calculations"""
    portfolios_df = all_data['portfolios']
    assets_df = all_data['assets']
    indexes_df = all_data['indexes']

    metrics = {
        'available_dates': [],
        'total_values_by_date': {},
        'asset_allocations_by_date': {},
        'equity_allocations_by_date': {},
        'index_performance_by_date': {},
        'portfolio_details_by_date': {},
        'raw_assets_data_by_date': {}
    }

    # Extract available dates
    if not portfolios_df.empty and 'date' in portfolios_df.columns:
        metrics['available_dates'] = sorted(portfolios_df['date'].dropna().unique(), reverse=True)

    # Preprocess data for each date
    for date in metrics['available_dates']:
        # Portfolio totals and details
        portfolio_data = portfolios_df[portfolios_df['date'] == date].copy()
        if not portfolio_data.empty:
            portfolio_data['balance_numeric'] = pd.to_numeric(portfolio_data['balance'], errors='coerce').fillna(0)
            total_value = portfolio_data['balance_numeric'].sum()
            metrics['total_values_by_date'][date] = total_value

            # Calculate beta for each portfolio and add as a column
            assets_data_for_date = assets_df[assets_df['date'] == date].copy() if not assets_df.empty else pd.DataFrame()

            # Find the portfolio name column in the portfolios data
            portfolio_name_columns = ['portfolio', 'account', 'portfolio_name', 'account_name', 'name']
            portfolio_name_col = None

            for col in portfolio_name_columns:
                if col in portfolio_data.columns:
                    portfolio_name_col = col
                    break

            if portfolio_name_col is not None:
                # Calculate beta for each portfolio
                portfolio_data['beta'] = portfolio_data[portfolio_name_col].apply(
                    lambda portfolio_name: calculate_portfolio_level_beta(assets_data_for_date, portfolio_name)
                )
            else:
                # If no portfolio name column found, set default beta
                portfolio_data['beta'] = 1.0

            metrics['portfolio_details_by_date'][date] = portfolio_data

        # Asset allocation
        assets_data = assets_df[assets_df['date'] == date].copy()
        if not assets_data.empty:
            # Store raw assets data for beta calculation
            metrics['raw_assets_data_by_date'][date] = assets_data.copy()

            assets_data['balance'] = pd.to_numeric(assets_data['balance'], errors='coerce').fillna(0)
            asset_allocation = assets_data.groupby('asset_class')['balance'].sum().reset_index()
            total_balance = asset_allocation['balance'].sum()
            if total_balance > 0:
                asset_allocation['percentage'] = (asset_allocation['balance'] / total_balance * 100).round(1)
                metrics['asset_allocations_by_date'][date] = asset_allocation

            # Equity allocation
            equity_data = assets_data[assets_data['asset_class'].str.lower() == 'equity'].copy()
            if not equity_data.empty:
                equity_allocation = equity_data.groupby('equity_class')['balance'].sum().reset_index()
                total_equity = equity_allocation['balance'].sum()
                if total_equity > 0:
                    equity_allocation['percentage'] = (equity_allocation['balance'] / total_equity * 100).round(1)
                    metrics['equity_allocations_by_date'][date] = equity_allocation

        # Index performance
        index_data = indexes_df[indexes_df['date'] == date].copy()
        if not index_data.empty:
            index_data['return_pct_ytd'] = pd.to_numeric(index_data['return_pct_ytd'], errors='coerce')
            metrics['index_performance_by_date'][date] = index_data

    return metrics


def prepare_portfolio_performance_data(all_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Prepare portfolio data for stacked bar chart showing group allocation over time"""
    portfolios_df = all_data['portfolios']

    if portfolios_df.empty:
        return pd.DataFrame()

    # Convert date column to datetime
    portfolios_df = portfolios_df.copy()
    portfolios_df['date'] = pd.to_datetime(portfolios_df['date'])

    # Convert balance to numeric
    portfolios_df['balance'] = pd.to_numeric(portfolios_df['balance'], errors='coerce').fillna(0)

    # Group by date and group, summing the balances
    grouped_data = portfolios_df.groupby(['date', 'group'])['balance'].sum().reset_index()

    # Calculate total portfolio value by date for percentage calculation
    total_by_date = grouped_data.groupby('date')['balance'].sum().reset_index()
    total_by_date.columns = ['date', 'total_balance']

    # Merge to get percentages
    grouped_data = grouped_data.merge(total_by_date, on='date')
    grouped_data['percentage'] = (grouped_data['balance'] / grouped_data['total_balance'] * 100).round(1)

    # Sort by date for proper chart display
    grouped_data = grouped_data.sort_values('date')

    return grouped_data