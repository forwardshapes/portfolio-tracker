import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("Portfolio Tracker")
st.write("Welcome to your portfolio tracking app!")

# Create connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Read data from Google Sheets
    df = conn.read(ttl="10m")  # Cache for 10 minutes

    if not df.empty:
        st.header("📊 Portfolio Overview")

        # Display the data
        st.subheader("Current Holdings")
        st.dataframe(df, use_container_width=True)

        # Show basic stats if numeric columns exist
        numeric_columns = df.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 0:
            st.subheader("📈 Portfolio Summary")
            col1, col2, col3 = st.columns(3)

            with col1:
                if 'value' in df.columns or 'Value' in df.columns:
                    value_col = 'value' if 'value' in df.columns else 'Value'
                    total_value = df[value_col].sum()
                    st.metric("Total Portfolio Value", f"${total_value:,.2f}")

            with col2:
                st.metric("Total Holdings", len(df))

            with col3:
                if 'quantity' in df.columns or 'Quantity' in df.columns:
                    qty_col = 'quantity' if 'quantity' in df.columns else 'Quantity'
                    total_shares = df[qty_col].sum()
                    st.metric("Total Shares", f"{total_shares:,.0f}")

        # Show sample chart if price data exists
        price_columns = [col for col in df.columns if 'price' in col.lower()]
        if price_columns:
            st.subheader("📊 Holdings Distribution")
            if 'symbol' in df.columns or 'Symbol' in df.columns:
                symbol_col = 'symbol' if 'symbol' in df.columns else 'Symbol'
                st.bar_chart(df.set_index(symbol_col)[price_columns[0]])

    else:
        st.warning("No data found in your Google Sheet. Make sure you have data in the first worksheet.")
        st.info("💡 **Tip**: Add column headers like 'Symbol', 'Quantity', 'Price', 'Value' to get the most out of your portfolio tracker!")

except Exception as e:
    st.error("❌ Unable to connect to Google Sheets")
    st.error(f"Error: {str(e)}")

    st.subheader("🔧 Troubleshooting")
    st.write("Make sure you have:")
    st.write("1. ✅ Shared your Google Sheet with your service account email")
    st.write("2. ✅ Added data to your Google Sheet")
    st.write("3. ✅ Configured your secrets.toml file correctly")

    st.info("**Service account email**: streamlit-portfolio-tracker@portfolio-tracker-473416.iam.gserviceaccount.com")
