import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import io

# --- PAGE CONFIGURATION ---
# Sets the browser tab title, favicon icon, and expands the layout to full width
st.set_page_config(
    page_title="Migdal Client Analytics",
    page_icon="Icon.ico",
    layout="wide"
)

# --- HELPER FUNCTIONS ---
def get_base64_img(file_path):
    """Loads a local image and converts it to base64 for embedding in HTML."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

@st.cache_data
def generate_corrected_excel(df):
    """Sorts data by Join Date, assigns new sequential client_ids (C1000+), and exports to Excel."""
    export_df = df.copy()
    
    # 1. Sort chronologically by Join Date (assuming it is datetime because of load_data)
    export_df = export_df.sort_values(by='תאריך_הצטרפות', ascending=True)
    
    # 2. Re-assign client_id starting from C1000
    export_df['client_id'] = [f"C{1000 + i}" for i in range(len(export_df))]
    
    # 3. Format dates back to string format for the Excel output matching the original CSV format
    export_df['תאריך_הצטרפות'] = export_df['תאריך_הצטרפות'].dt.strftime('%d/%m/%Y')
    export_df['תאריך_נטישה'] = export_df['תאריך_נטישה'].dt.strftime('%d/%m/%Y').fillna('')
    
    # Write to an in-memory BytesIO buffer as Excel using openpyxl
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Corrected Data')
        
    return output.getvalue()

# --- CUSTOM STYLING ---
# Injecting subtle CSS to give metric cards a clean, executive look
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- DATA INGESTION ---
@st.cache_data
def load_data():
    """Reads the client dataset and performs initial date parsing."""
    # Note: File path assumes 'data' folder structure as organized by user
    df = pd.read_csv("data/clients_data.csv")
    
    # Converting Hebrew date strings to Python datetime objects for time-series analysis
    df['תאריך_הצטרפות'] = pd.to_datetime(df['תאריך_הצטרפות'], format='%d/%m/%Y', errors='coerce')
    df['תאריך_נטישה'] = pd.to_datetime(df['תאריך_נטישה'], format='%d/%m/%Y', errors='coerce')
    return df

# Initialize data loading with basic error handling
try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file not found. Please ensure 'data/clients_data.csv' exists.")
    st.stop()

# --- HEADER SECTION ---
st.title("📊 Migdal Executive Dashboard")

# --- SIDEBAR FILTERS ---
# Displaying a small, circular company icon in the sidebar
with st.sidebar:
    logo_base64 = get_base64_img("Icon.ico")
    if logo_base64:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 20px;">
                <img src="data:image/x-icon;base64,{logo_base64}" 
                     style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; pointer-events: none;">
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # --- TASK B: DATA CORRECTION ---
    st.subheader("Data Correction")
    st.write("Chronologically sorts 'Join Dates' and re-assigns `client_id`s starting at `C1000`.")
    excel_data = generate_corrected_excel(df)
    st.download_button(
        label="📥 Download Corrected Excel",
        data=excel_data,
        file_name="corrected_clients_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.markdown("---")

# These allow the CEO to slice the data by their primary categories
st.sidebar.header("Filter Data")

city_filter = st.sidebar.multiselect("City (עיר)", options=df['עיר'].unique(), default=df['עיר'].unique())
service_filter = st.sidebar.multiselect("Service Type (סוג שירות)", options=df['סוג_שירות'].unique(), default=df['סוג_שירות'].unique())
status_filter = st.sidebar.multiselect("Status (סטטוס)", options=df['סטטוס'].unique(), default=df['סטטוס'].unique())

# Application of filters to the main dataframe
filtered_df = df[
    (df['עיר'].isin(city_filter)) &
    (df['סוג_שירות'].isin(service_filter)) &
    (df['סטטוס'].isin(status_filter))
]

# --- KEY PERFORMANCE INDICATORS (KPIs) ---
# High-level metrics displayed in a 4-column row for immediate impact
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Clients", f"{len(filtered_df):,}")
col2.metric("Active Clients", f"{len(filtered_df[filtered_df['סטטוס'] == 'פעיל']):,}")
col3.metric("Avg Satisfaction", f"{filtered_df['שביעות_רצון'].mean():.1f}/10")
col4.metric("Total Portfolio (NIS)", f"₪{filtered_df['סכום_תיק'].sum():,.0f}")

st.markdown("---")

# --- VISUALIZATIONS ---
chart_cols = st.columns(2)

with chart_cols[0]:
    # Distribution Chart: Viewing how satisfied clients are on a scale of 1-10
    st.subheader("Satisfaction Distribution")
    fig_sat = px.histogram(filtered_df, x="שביעות_רצון", nbins=10, 
                           title="Client Satisfaction Rating",
                           labels={"שביעות_רצון": "Satisfaction (1-10)"},
                           color_discrete_sequence=["#2E86C1"])
    fig_sat.update_layout(bargap=0.1)
    # Applying 'stretch' to use full container width as per latest Streamlit standards
    st.plotly_chart(fig_sat, width="stretch")

with chart_cols[1]:
    # Trend Chart: Visualizing churn events over time to identify negative patterns
    st.subheader("Churn Over Time")
    churn_df = filtered_df.dropna(subset=['תאריך_נטישה']).copy()
    if not churn_df.empty:
        # Re-sampling data to Monthly frequency for a smoother trend line
        churn_df['Month-Year'] = churn_df['תאריך_נטישה'].dt.to_period('M')
        churn_counts = churn_df.groupby('Month-Year').size().reset_index(name='Churns')
        churn_counts['Month-Year'] = churn_counts['Month-Year'].dt.to_timestamp()
        churn_counts = churn_counts.sort_values('Month-Year')
        
        fig_churn = px.line(churn_counts, x="Month-Year", y="Churns", 
                            title="Monthly Churns", markers=True,
                            color_discrete_sequence=["#E74C3C"])
        # Applying 'stretch' to use full container width
        st.plotly_chart(fig_churn, width="stretch")
    else:
        st.info("No churn data available for current filters.")

# --- DATA EXPLORATION ---
st.markdown("---")
with st.expander("Raw Data Sample", expanded=False):
    # Displaying the top 100 results for a quick sanity check of the values
    st.dataframe(filtered_df.head(100))
