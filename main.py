import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Andrei's Portfolio",
    page_icon="📈"
)

st.title("📈 Andrei's Portfolio")

# Create connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_portfolio_data():
    """Load current portfolio holdings from the main sheet"""
    try:
        df = conn.read(ttl="10m", worksheet="Holdings")
        if not df.empty:
            # Verify required columns exist
            required_cols = ['Date', 'Portfolio', 'Symbol', 'Asset_Group', 'Quantity', 'Price', 'Value']
            if all(col in df.columns for col in required_cols):
                return df
        return None
    except:
        try:
            # Fallback to default worksheet if "Holdings" doesn't exist
            df = conn.read(ttl="10m")
            return df if not df.empty else None
        except:
            return None

def load_performance_data():
    """Load monthly performance data from Performance sheet"""
    try:
        df = conn.read(ttl="10m", worksheet="Performance")
        if not df.empty:
            required_cols = ['Date', 'Portfolio_Value', 'Portfolio_Beta', '%_Cash']
            if all(col in df.columns for col in required_cols):
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                return df
    except:
        pass
    return None

def load_portfolio_summary():
    """Load portfolio summary data for the data table"""
    try:
        df = conn.read(ttl="10m", worksheet="Summary")
        if not df.empty:
            required_cols = ['Date', 'Portfolio', 'Value', 'Strategy', 'Beta']
            if all(col in df.columns for col in required_cols):
                return df
    except:
        pass
    return None

def get_latest_performance_metrics():
    """Get the latest performance metrics from the most recent date"""
    performance_df = load_performance_data()
    if performance_df is not None and not performance_df.empty:
        # Get the row with the maximum date
        latest_row = performance_df.loc[performance_df['Date'].idxmax()]

        # Convert to numeric values to handle string data from sheets
        try:
            # Debug: Check what we're getting from the sheet
            portfolio_value = pd.to_numeric(str(latest_row['Portfolio_Value']).replace(',', '').replace('$', ''), errors='coerce')
            portfolio_beta = pd.to_numeric(str(latest_row['Portfolio_Beta']).replace(',', ''), errors='coerce')
            cash_pct = pd.to_numeric(str(latest_row['%_Cash']).replace('%', '').replace(',', ''), errors='coerce')

            return {
                'Portfolio_Value': portfolio_value if pd.notna(portfolio_value) else 0,
                'Portfolio_Beta': portfolio_beta if pd.notna(portfolio_beta) else 0,
                'Cash_Pct': cash_pct if pd.notna(cash_pct) else 0,
                'Date': latest_row['Date']
            }
        except Exception as e:
            return None
    return None

try:
    # Load all data
    holdings_df = load_portfolio_data()
    performance_df = load_performance_data()
    summary_df = load_portfolio_summary()
    latest_metrics = get_latest_performance_metrics()

    # Add date indicator right below title
    if latest_metrics:
        st.caption(f"📅 Data as of {latest_metrics['Date'].strftime('%B %d, %Y')}")
    else:
        st.caption("📅 Performance data not available")

    # === HOMEPAGE LAYOUT ===

    # 1. Portfolio Summary
    st.markdown("### 📊 Portfolio Summary")
    col1, col2, col3 = st.columns(3)

    if latest_metrics:
        with col1:
            st.metric(
                label="Total Value",
                value=f"${latest_metrics['Portfolio_Value']:,.0f}",
                delta=None
            )

        with col2:
            st.metric(
                label="Beta",
                value=f"{latest_metrics['Portfolio_Beta']:.2f}",
                delta=None
            )

        with col3:
            st.metric(
                label="% in Cash",
                value=f"{latest_metrics['Cash_Pct']:.1f}%",
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

    # 2. Monthly Performance Chart
    st.markdown("### 📊 Portfolio Performance (2025)")

    if performance_df is not None:
        # Filter data from Jan 1, 2025 onwards
        start_date = datetime(2025, 1, 1)
        chart_data = performance_df[performance_df['Date'] >= start_date].copy()

        if not chart_data.empty:
            # Prepare data for line chart
            chart_data = chart_data.set_index('Date')
            st.line_chart(chart_data[['Portfolio_Value']], use_container_width=True)
        else:
            st.info("📅 No performance data available from January 1, 2025. Add monthly data to the 'Performance' sheet with columns: Date, Portfolio_Value")
    else:
        st.info("📊 Create a 'Performance' sheet with columns: Date, Portfolio_Value, Portfolio_Beta, %_Cash to track monthly performance")

    st.markdown("---")

    # 3. Asset Allocation Pie Chart
    st.markdown("### 🥧 Asset Allocation")
    if holdings_df is not None:
        # Convert Value column to numeric to handle string data from sheets
        holdings_df_numeric = holdings_df.copy()
        holdings_df_numeric['Value'] = pd.to_numeric(holdings_df_numeric['Value'], errors='coerce').fillna(0)

        # Calculate Asset_Group allocation
        asset_allocation = holdings_df_numeric.groupby('Asset_Group')['Value'].sum().reset_index()
        asset_allocation['Percentage'] = (asset_allocation['Value'] / asset_allocation['Value'].sum() * 100).round(1)

        if not asset_allocation.empty and asset_allocation['Value'].sum() > 0:
            # Create pie chart using Plotly
            fig = px.pie(asset_allocation,
                        values='Value',
                        names='Asset_Group',
                        title='Portfolio Asset Allocation')
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            # Show allocation table
            col1, col2 = st.columns(2)
            with col1:
                display_allocation = asset_allocation.copy()
                display_allocation['Value'] = display_allocation['Value'].apply(lambda x: f"${float(x):,.0f}")
                display_allocation['Percentage'] = display_allocation['Percentage'].apply(lambda x: f"{float(x)}%")
                st.dataframe(display_allocation, use_container_width=True, hide_index=True)
        else:
            st.info("No asset allocation data available")
    else:
        st.info("📊 Holdings data needed to show asset allocation")

    st.markdown("---")

    # 4. Portfolio Details Table
    st.markdown("### 📋 Portfolio Details")

    if summary_df is not None:
        # Simple formatting for display
        display_df = summary_df.copy()

        # Format Value as currency
        if 'Value' in display_df.columns:
            display_df['Value'] = pd.to_numeric(display_df['Value'], errors='coerce')
            display_df['Value'] = display_df['Value'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else x)

        # Format Beta to 2 decimal places
        if 'Beta' in display_df.columns:
            display_df['Beta'] = pd.to_numeric(display_df['Beta'], errors='coerce')
            display_df['Beta'] = display_df['Beta'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else x)

        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("📊 Create a 'Summary' sheet with columns: Date, Portfolio, Value, Strategy, Beta for detailed portfolio breakdown")

    # === DATA SETUP GUIDANCE ===
    if holdings_df is None and performance_df is None and summary_df is None:
        st.markdown("---")
        st.markdown("### 🚀 Getting Started")
        st.warning("No data sheets found. Set up your Google Sheets with the following structure:")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📊 Holdings Sheet:**")
            st.code("Date | Portfolio | Symbol | Asset_Group | Quantity | Price | Value")

        with col2:
            st.markdown("**📈 Performance Sheet:**")
            st.code("Date | Portfolio_Value | Portfolio_Beta | %_Cash")

        with col3:
            st.markdown("**📋 Summary Sheet:**")
            st.code("Date | Portfolio | Value | Strategy | Beta")

except Exception as e:
    st.error("❌ Unable to connect to Google Sheets")
    st.error(f"Error: {str(e)}")

    st.markdown("---")
    st.subheader("🔧 Troubleshooting")
    st.write("Make sure you have:")
    st.write("1. ✅ Shared your Google Sheet with your service account email")
    st.write("2. ✅ Created the required worksheets (Holdings, Performance, Summary)")
    st.write("3. ✅ Added data with the correct column headers")
    st.write("4. ✅ Configured your secrets.toml file correctly")

    st.info("**Service account email**: streamlit-portfolio-tracker@portfolio-tracker-473416.iam.gserviceaccount.com")