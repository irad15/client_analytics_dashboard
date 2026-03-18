**Tools used:** Python served as the core language. Streamlit was chosen to rapidly build an interactive web app without writing custom HTML/JS. Pandas handles the chronological data sorting efficiently, Plotly powers the responsive charts, and openpyxl generates the native Excel exports.

**Dashboard display:** Features an executive UI with four key metrics, sidebar filters, a satisfaction histogram, and a monthly churn trend chart.

**Data correction logic:** Pandas converts `תאריך_הצטרפות` to datetime and sorts the dataset strictly chronologically. 
Sequential `client_id`s starting from `C1000` are then mapped onto the sorted rows. 
The corrected dataframe is generated as an in-memory Excel file and provided via a one-click download button.
