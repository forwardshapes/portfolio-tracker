#  Portfolio Tracker

A Streamlit web application for tracking a personal investment portfolio using Google Sheets as the data source.

## Features

- **Real-time Portfolio Tracking**: Connect to Google Sheets to view your portfolio data
- **Interactive Visualizations**:
  - Portfolio value over time (stacked bar charts)
  - Asset allocation by class (pie charts)
  - Equity allocation breakdown
- **Performance Metrics**:
  - Total portfolio value
  - Portfolio beta calculation
  - Cash percentage tracking
  - Comparison with S&P 500 and NASDAQ indices
- **Multi-date Support**: View historical snapshots of your portfolio
- **Responsive Design**: Clean, mobile-friendly interface

## Screenshots

**Portfolio Summary**
![Portfolio Summary](https://tradingnotions.com/wp-content/uploads/2025/10/01-portfolio-summary.png)

**Portfolio Value over time**
![Portfolio Summary](https://tradingnotions.com/wp-content/uploads/2025/10/02-portfolio-value-over-time.png)

**Asset Allocation**
![Portfolio Summary](https://tradingnotions.com/wp-content/uploads/2025/10/03-asset-allocation.png)

**Portfolio Details**
![Portfolio Summary](https://tradingnotions.com/wp-content/uploads/2025/10/04-portfolio-details.png)

## Prerequisites

- Python 3.13 or higher
- A Google Cloud Platform account (for Google Sheets API access)
- A Google Sheet with your portfolio data

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/portfolio-tracker.git
   cd portfolio-tracker
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Set up Google Sheets API**

   a. Create a project in [Google Cloud Console](https://console.cloud.google.com/)

   b. Enable the Google Sheets API

   c. Create a service account and download the JSON credentials file

   d. Share your Google Sheet with the service account email

4. **Configure secrets**

   ```bash
   cp .streamlit/secrets.toml.template .streamlit/secrets.toml
   ```

   Edit `.streamlit/secrets.toml` and add:
   - Your Google Sheet URL
   - Service account credentials from the JSON file
   - (Optional) Your name for the portfolio title

## Google Sheets Template

Make a copy of this [Google Sheets template](https://docs.google.com/spreadsheets/d/1bejdPXweFLePzXjy_LEjYyflpRWbxbdDiGrs7d-nCJA/edit?gid=0#gid=0) 

Go to **File → Make a copy** to save it to your own Google Drive.

## Usage

Run the Streamlit app:

```bash
uv run streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Project Structure

```
portfolio-tracker/
├── main.py                          # Main Streamlit application
├── modules/
│   ├── __init__.py
│   ├── config.py                    # Configuration settings
│   ├── data_loader.py               # Google Sheets data loading
│   ├── portfolio_metrics.py         # Portfolio calculations
│   └── utils.py                     # Utility functions
├── .streamlit/
│   ├── secrets.toml.template        # Template for credentials
│   └── secrets.toml                 # Your actual credentials (not in git)
├── docs/                            # Documentation files
├── pyproject.toml                   # Project dependencies
└── README.md
```

## Key Metrics Explained

- **Total Value**: Sum of all portfolio balances
- **Beta**: Weighted average volatility relative to the market (1.0 = market volatility)
- **% in Cash**: Percentage of portfolio in cash or money market instruments
- **YTD Returns**: Year-to-date performance for comparison with market indices

## Development

### Adding New Features

1. Data loading functions go in `modules/data_loader.py`
2. Calculation logic goes in `modules/portfolio_metrics.py`
3. Display formatting goes in `modules/utils.py`
4. Configuration constants go in `modules/config.py`

### Caching

The app uses Streamlit's `@st.cache_data` decorator with a 10-minute TTL to minimize Google Sheets API calls.

## Troubleshooting

**Issue**: "Error loading data: Permission denied"
- **Solution**: Make sure you've shared your Google Sheet with the service account email

**Issue**: "No module named 'streamlit_gsheets'"
- **Solution**: Run `uv sync` or `pip install st-gsheets-connection`

**Issue**: "No dates available from portfolios sheet"
- **Solution**: Check that your Google Sheet has a `portfolios` worksheet with a `date` column

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualizations powered by [Plotly](https://plotly.com/)
- Google Sheets integration via [st-gsheets-connection](https://github.com/streamlit/gsheets-connection)
- Built with [Claude Code](https://www.claude.com/product/claude-code)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/portfolio-tracker/issues) on GitHub.

---

**Note**: This application is for personal portfolio tracking purposes. Past performance does not guarantee future results. Always consult with a financial advisor for investment decisions.
