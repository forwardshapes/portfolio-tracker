"""
Portfolio metrics calculation functions.
"""

import pandas as pd
from typing import Dict, Optional


def calculate_total_portfolio_value(portfolio_metrics: Dict, selected_date) -> float:
    """Calculate total portfolio value for a given date"""
    if selected_date in portfolio_metrics['total_values_by_date']:
        return portfolio_metrics['total_values_by_date'][selected_date]
    return 0.0


def calculate_cash_percentage(portfolio_metrics: Dict, selected_date) -> float:
    """Calculate percentage of portfolio in cash/money market instruments"""
    if selected_date not in portfolio_metrics['asset_allocations_by_date']:
        return 0.0

    asset_allocation = portfolio_metrics['asset_allocations_by_date'][selected_date]
    cash_rows = asset_allocation[asset_allocation['asset_class'].str.lower().isin(['cash', 'money market'])]

    if not cash_rows.empty:
        return cash_rows['percentage'].sum()
    return 0.0


def calculate_portfolio_beta(portfolio_metrics: Dict, selected_date) -> float:
    """
    Calculate portfolio beta as weighted average of individual asset betas.

    Beta measures the volatility of the portfolio relative to the market.
    This calculation uses the balance-weighted average of individual asset betas.
    """
    # Get the raw assets data for the selected date
    all_data = portfolio_metrics.get('raw_assets_data_by_date', {})
    assets_data = all_data.get(selected_date)

    if assets_data is None or assets_data.empty:
        return 1.0  # Default market beta if no data

    # Ensure we have the required columns
    if 'beta' not in assets_data.columns or 'balance' not in assets_data.columns:
        return 1.0  # Default if beta column doesn't exist

    # Convert balance and beta to numeric, handling any conversion errors
    assets_data = assets_data.copy()
    assets_data['balance_numeric'] = pd.to_numeric(assets_data['balance'], errors='coerce').fillna(0)
    assets_data['beta_numeric'] = pd.to_numeric(assets_data['beta'], errors='coerce').fillna(1.0)

    # Filter out rows with zero or negative balances
    valid_assets = assets_data[assets_data['balance_numeric'] > 0].copy()

    if valid_assets.empty:
        return 1.0

    # Calculate total portfolio value
    total_value = valid_assets['balance_numeric'].sum()

    if total_value <= 0:
        return 1.0

    # Calculate weights (each asset's percentage of total portfolio)
    valid_assets['weight'] = valid_assets['balance_numeric'] / total_value

    # Calculate weighted average beta
    weighted_beta = (valid_assets['weight'] * valid_assets['beta_numeric']).sum()

    # Validate the result
    if pd.isna(weighted_beta) or weighted_beta <= 0:
        return 1.0  # Default market beta for invalid results

    return round(weighted_beta, 2)


def calculate_portfolio_level_beta(assets_data: pd.DataFrame, portfolio_name: str) -> float:
    """
    Calculate beta for a specific portfolio/account based on its assets.

    Args:
        assets_data: DataFrame with assets data for a specific date
        portfolio_name: Name of the portfolio to calculate beta for

    Returns:
        Weighted average beta for the specified portfolio
    """
    if assets_data.empty:
        return 1.0

    # Filter assets for this specific portfolio
    # Assuming there's a 'portfolio' or 'account' column in assets data
    portfolio_columns = ['portfolio', 'account', 'portfolio_name', 'account_name']
    portfolio_col = None

    for col in portfolio_columns:
        if col in assets_data.columns:
            portfolio_col = col
            break

    if portfolio_col is None:
        # If no portfolio column found, return 1.0 as default
        return 1.0

    # Filter for this specific portfolio
    portfolio_assets = assets_data[assets_data[portfolio_col] == portfolio_name].copy()

    if portfolio_assets.empty:
        return 1.0

    # Ensure we have required columns
    if 'beta' not in portfolio_assets.columns or 'balance' not in portfolio_assets.columns:
        return 1.0

    # Convert to numeric
    portfolio_assets['balance_numeric'] = pd.to_numeric(portfolio_assets['balance'], errors='coerce').fillna(0)
    portfolio_assets['beta_numeric'] = pd.to_numeric(portfolio_assets['beta'], errors='coerce').fillna(1.0)

    # Filter valid assets
    valid_assets = portfolio_assets[portfolio_assets['balance_numeric'] > 0].copy()

    if valid_assets.empty:
        return 1.0

    # Calculate total value for this portfolio
    total_value = valid_assets['balance_numeric'].sum()

    if total_value <= 0:
        return 1.0

    # Calculate weights and weighted beta
    valid_assets['weight'] = valid_assets['balance_numeric'] / total_value
    weighted_beta = (valid_assets['weight'] * valid_assets['beta_numeric']).sum()

    # Validate result
    if pd.isna(weighted_beta) or weighted_beta <= 0:
        return 1.0

    return round(weighted_beta, 2)


def get_sp500_performance(portfolio_metrics: Dict, selected_date) -> Optional[float]:
    """Get S&P 500 YTD performance for comparison"""
    if selected_date not in portfolio_metrics['index_performance_by_date']:
        return None

    index_data = portfolio_metrics['index_performance_by_date'][selected_date]
    sp500_row = index_data[index_data['index'].str.lower() == 'sp500']

    if not sp500_row.empty:
        return sp500_row.iloc[0]['return_pct_ytd'] * 100  # Convert to percentage
    return None