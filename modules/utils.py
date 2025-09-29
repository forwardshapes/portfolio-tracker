"""
Utility functions for data formatting and processing in the portfolio tracker.
"""

import pandas as pd
from typing import List


def format_currency(value: float) -> str:
    """Format numeric value as currency string"""
    if pd.isna(value):
        return "--"
    return f"${value:,.0f}"


def format_percentage(value: float, multiply_by_100: bool = False) -> str:
    """Format numeric value as percentage string"""
    if pd.isna(value):
        return "--"
    display_value = value * 100 if multiply_by_100 else value
    return f"{display_value:.2f}%"


def format_beta_value(value: float) -> str:
    """Format beta value for display"""
    if pd.isna(value):
        return "--"
    return f"{value:.2f}"


def format_dataframe_for_display(
    df: pd.DataFrame,
    currency_cols: List[str] = None,
    percentage_cols: List[str] = None,
    beta_cols: List[str] = None
) -> pd.DataFrame:
    """Apply standard formatting to dataframe columns"""
    display_df = df.copy()

    if currency_cols:
        for col in currency_cols:
            if col in display_df.columns:
                display_df[col] = pd.to_numeric(display_df[col], errors='coerce')
                display_df[col] = display_df[col].apply(format_currency)

    if percentage_cols:
        for col in percentage_cols:
            if col in display_df.columns:
                display_df[col] = pd.to_numeric(display_df[col], errors='coerce')
                display_df[col] = display_df[col].apply(lambda x: format_percentage(x, multiply_by_100=True))

    if beta_cols:
        for col in beta_cols:
            if col in display_df.columns:
                display_df[col] = pd.to_numeric(display_df[col], errors='coerce')
                display_df[col] = display_df[col].apply(format_beta_value)

    return display_df


def capitalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Capitalize and format column names for display"""
    df_copy = df.copy()
    df_copy.columns = [col.replace('_', ' ').title() for col in df_copy.columns]
    return df_copy