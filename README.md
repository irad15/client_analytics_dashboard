# Migdal Client Analytics Dashboard

An interactive Streamlit dashboard built for Migdal Financial Services to analyze customer data and correct system ID issues.

## Project Description
This application was built using **Python, Streamlit, Pandas, Plotly**, and **openpyxl** for Excel exports. 
- **Dashboard (Task A)**: Features an executive-level UI with metric cards (Total Clients, Active, Avg Satisfaction, Portfolio Value), sidebar filters (City, Service, Status), and interactive Plotly visualizations for satisfaction distribution and monthly churn trends. 
- **Data Correction (Task B)**: Implemented a chronological re-ordering engine. It converts Join Dates to datetime objects, sorts the entire dataset, and re-assigns `client_id`s starting from `C1000` to ensure ID order matches join order. This is accessible via a one-click Excel download button in the sidebar.

## Installation & Running
Developed using `uv` for modern, fast dependency management.

```bash
# Set up virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt

# Run the app
uv run streamlit run app.py
```
