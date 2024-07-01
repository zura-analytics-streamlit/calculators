import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import base64

# Set page configuration
st.set_page_config(layout="wide")  # Set wide layout for Streamlit app

# Function to download sample_data_formats.txt
def download_sample_data():
    # Define sample formats for different data types
    sample_operating_data = """
-----------------------Sample_Operating_Data------------------------------
FORMAT OF "CSV(sample Format)":
PumpID,Date,Operating Hours
1,2024-06-01,120
1,2024-06-02,115
2,2024-06-01,105
2,2024-06-02,110
==================================================================
FORMAT OF "JSON (sample Format)":

[
    {
        "PumpID": 1,
        "Date": "2024-06-01",
        "OperatingHours": 120
    },
    {
        "PumpID": 1,
        "Date": "2024-06-02",
        "OperatingHours": 115
    },
    {
        "PumpID": 2,
        "Date": "2024-06-01",
        "OperatingHours": 105
    },
    {
        "PumpID": 2,
        "Date": "2024-06-02",
        "OperatingHours": 110
    }
]
==================================================================
FORMAT OF "Excel files (XLSX sample Format) ":

PumpID|Date|Operating Hours
1|2024-06-01|120
1|2024-06-02|115
2|2024-06-01|105
2|2024-06-02|110
    ==================================================================
    """

    sample_vibration_data = """
--------------------FORMAT OF Vibration Data------------------------------
FORMAT OF "Vibration Data (CSV Sample Format)":

PumpID,Date,Vibration Level (mm/s)
1,2024-06-01 08:00:00,0.5
1,2024-06-01 08:01:00,0.6
2,2024-06-01 08:00:00,0.7
2,2024-06-01 08:01:00,0.8
    ==================================================================
FORMAT OF "JSON (sample Format)":

[
    {
        "PumpID": 1,
        "Date": "2024-06-01 08:00:00",
        ",Vibration Level (mm/s)": 0.5
    },
    {
        "PumpID": 1,
        "Date": "2024-06-01 08:01:00",
        ",Vibration Level (mm/s)":0.6
    },
    {
        "PumpID": 2,
        "Date": "2024-06-01 08:00:00",
        ",Vibration Level (mm/s)": 0.7
    },
    {
        "PumpID": 2,
        "Date": "2024-06-01 08:01:00",
        ",Vibration Level (mm/s)": 0.8
    }
]
==================================================================
FORMAT OF "Excel files (XLSX sample Format) ":

PumpID|Date     |Vibration Level (mm/s)
1|2024-06-01 08:00:00|0.5
1|2024-06-02 08:00:00|0.6
2|2024-06-01 08:00:00|0.7
2|2024-06-02 08:00:00|0.8

    """

    sample_maintenance_data = """
-------------------FORMAT OF Maintenance History------------------------------
FORMAT OF "Maintenance History (CSV Sample Format)":

PumpID,Failure Date,Description
1,2024-06-01,Change oil
1,2024-06-02,Replace bearings
2,2024-06-01,Clean filters
2,2024-06-02,Inspect seals
==================================================================
FORMAT OF "JSON (sample Format)":

[
    {
        "PumpID": 1,
        "Failure Date": "2024-06-01",
        "Description": Change oil
    },
    {
        "PumpID": 1,
        "Failure Date": "2024-06-02",
        "Description": Replace bearings
    },
    {
        "PumpID": 2,
        "Failure Date": "2024-06-01",
        "Description": Clean filters
    },
    {
        "PumpID": 2,
        "Failure Date": "2024-06-02",
        "Description": Inspect seals
    }
]
==================================================================
FORMAT OF "Excel files (XLSX sample Format) ":

PumpID| Failure Date|Description
1     | 2024-06-01  |   Change oil
1     | 2024-06-02  |   Replace bearings
2     | 2024-06-01  |   Clean filters
2     | 2024-06-02  |   Inspect seals
    """

    # Encoding content to base64
    content = (sample_operating_data + sample_vibration_data + sample_maintenance_data).encode()
    b64 = base64.b64encode(content).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/txt;base64,{b64}" download="sample_data_formats.txt">Download sample_data_formats.txt</a>'
    return href

# Function to calculate MTBF
def calculate_mtbf(operating_data, maintenance_data):
    # Sum of operating hours per pump
    total_operating_time = operating_data.groupby('PumpID')['Operating Hours'].sum().reset_index()

    # Count of failures per pump
    num_failures = maintenance_data.groupby('PumpID').size().reset_index(name='Number of Failures')

    # Merge the two dataframes
    mtbf_data = pd.merge(total_operating_time, num_failures, on='PumpID', how='outer')

    # Calculate MTBF rounded and without decimal values
    mtbf_data['MTBF (Hours)'] = mtbf_data['Operating Hours'] // mtbf_data['Number of Failures']

    return mtbf_data

# Function to calculate Remaining Useful Life (RUL)
def calculate_rul(mtbf_data, rul_factor):
    # Calculate RUL as MTBF times a factor
    mtbf_data['RUL (Hours)'] = mtbf_data['MTBF (Hours)'] * rul_factor
    
    # Round RUL (Hours) and display without decimal values
    mtbf_data['RUL (Hours)'] = mtbf_data['RUL (Hours)'].astype(int)

    # Normalize RUL to percentage
    mtbf_data['RUL (%)'] = (mtbf_data['RUL (Hours)'] / mtbf_data['RUL (Hours)'].max()) * 100
    # Round RUL (%) to 2 decimal places
    mtbf_data['RUL (%)'] = mtbf_data['RUL (%)'].round(2)

    return mtbf_data


# Function to calculate Remaining Useful Life (RUL)
def calculate_rul(mtbf_data, rul_factor):
    # Calculate RUL as MTBF times a factor
    mtbf_data['RUL (Hours)'] = mtbf_data['MTBF (Hours)'] * rul_factor
    
    # Normalize RUL to percentage
    mtbf_data['RUL (%)'] = (mtbf_data['RUL (Hours)'] / mtbf_data['RUL (Hours)'].max()) * 100
    # Round RUL (%) to 2 decimal places
    mtbf_data['RUL (%)'] = mtbf_data['RUL (%)'].round(2)
    return mtbf_data

def upload_and_process_data():
    operating_data = None
    vibration_data = None
    maintenance_data = None

    # Input for RUL Factor
    rul_factor = st.sidebar.slider('RUL Factor', min_value=0.1, max_value=2.0, value=1.0, step=0.1)

    # Dropdown for PumpID selection
    with st.sidebar.expander("Upload Data Files"):
        #st.header('Upload Data Files')
        operating_file = st.file_uploader('Operating Data ', type=['csv', 'json', 'xlsx'])
        vibration_file = st.file_uploader('Vibration Data ', type=['csv', 'json', 'xlsx'])
        maintenance_file = st.file_uploader('Maintenance History ', type=['csv', 'json', 'xlsx'])
        st.sidebar.markdown(download_sample_data(), unsafe_allow_html=True)

    # File uploads
    if operating_file is not None:
        try:
            if operating_file.type == 'application/vnd.ms-excel' or operating_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                operating_data = pd.read_excel(operating_file, engine='openpyxl')
            elif operating_file.type == 'application/json':
                operating_data = pd.read_json(operating_file)
            else:
                operating_data = pd.read_csv(operating_file)
            
            # Attempt to parse the 'Date' column correctly
            if 'Date' in operating_data.columns:
                operating_data['Date'] = pd.to_datetime(operating_data['Date'], errors='coerce')
        except pd.errors.EmptyDataError:
            st.error('Uploaded Operating Data file is empty or could not be parsed.')

    if vibration_file is not None:
        try:
            if vibration_file.type == 'application/vnd.ms-excel' or vibration_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                vibration_data = pd.read_excel(vibration_file, engine='openpyxl')
            elif vibration_file.type == 'application/json':
                vibration_data = pd.read_json(vibration_file)
            else:
                vibration_data = pd.read_csv(vibration_file)
            
            # Attempt to parse the 'Date' column correctly
            if 'Date' in vibration_data.columns:
                vibration_data['Date'] = pd.to_datetime(vibration_data['Date'], errors='coerce')
        except pd.errors.EmptyDataError:
            st.error('Uploaded Vibration Data file is empty or could not be parsed.')

    if maintenance_file is not None:
        try:
            if maintenance_file.type == 'application/vnd.ms-excel' or maintenance_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                maintenance_data = pd.read_excel(maintenance_file, engine='openpyxl')
            elif maintenance_file.type == 'application/json':
                maintenance_data = pd.read_json(maintenance_file)
            else:
                maintenance_data = pd.read_csv(maintenance_file)
            
            # Attempt to parse the 'Failure Date' column correctly
            if 'Failure Date' in maintenance_data.columns:
                maintenance_data['Failure Date'] = pd.to_datetime(maintenance_data['Failure Date'], errors='coerce')
        except pd.errors.EmptyDataError:
            st.error('Uploaded Maintenance History file is empty or could not be parsed.')

    # Prepare pump_id_options based on available data
    if operating_data is not None:
        pump_id_options = ['All'] + operating_data['PumpID'].unique().tolist()
    else:
        pump_id_options = ['All']

    return operating_data, vibration_data, maintenance_data, rul_factor



def main():
    st.title('Pump Maintenance and Performance Analyzer')

    # Upload and process data files
    operating_data, vibration_data, maintenance_data, rul_factor = upload_and_process_data()



# Streamlit app layout
st.title('Pump Maintenance and Performance Analyzer')
st.markdown('<style>div.block-container{padding-top:2.2rem;}</style>', unsafe_allow_html=True)


# Download button for sample_data_formats.txt

#st.sidebar.markdown(download_sample_data(), unsafe_allow_html=True)

# Upload and process data
operating_data, vibration_data, maintenance_data, rul_factor = upload_and_process_data()

# Check if data is loaded successfully
if operating_data is not None and maintenance_data is not None and vibration_data is not None:
    try:
        # Ensure the uploaded files contain PumpID
        if 'PumpID' in operating_data.columns and 'PumpID' in maintenance_data.columns and 'PumpID' in vibration_data.columns:
            # Calculate MTBF
            mtbf_data = calculate_mtbf(operating_data, maintenance_data)

            # Calculate RUL
            mtbf_data = calculate_rul(mtbf_data, rul_factor)

            # Dropdown for PumpID selection
            st.sidebar.header('Filter Results by Pump ID')
            pump_id_options = ['All'] + operating_data['PumpID'].unique().tolist()
            selected_pump_id = st.sidebar.selectbox('Select Pump ID', pump_id_options)

            # Filter data based on selected Pump ID
            if selected_pump_id != 'All':
                mtbf_data = mtbf_data[mtbf_data['PumpID'] == selected_pump_id]
                if vibration_data is not None:
                    vibration_data = vibration_data[vibration_data['PumpID'] == selected_pump_id]
                if operating_data is not None:
                    operating_data = operating_data[operating_data['PumpID'] == selected_pump_id]

            # Layout: Combined Charts, gauge and table below
            st.header('MTBF Trends and Vibration Data')

            col1, col2 = st.columns([2, 2])

            with col1:
                #st.markdown('MTBF Trends Over Time')
                if 'Date' in operating_data.columns:
                    if selected_pump_id == 'All':
                        # Aggregate operating data by date
                        avg_mtbf_over_time = operating_data.groupby('Date')['Operating Hours'].mean().reset_index()
                        fig = px.line(avg_mtbf_over_time, x='Date', y='Operating Hours', title='Average MTBF Over Time')
                        fig.update_layout(width=550, height=300)  # Adjust width and height as needed
                        st.plotly_chart(fig)
                    else:
                        st.line_chart(operating_data.set_index('Date')['Operating Hours'])
                else:
                    st.error('Cannot parse dates in Operating Data. Please ensure they are in a valid format.')

            with col2:
                #st.markdown('Vibration Data Over Time')
                if vibration_data is not None and 'Date' in vibration_data.columns:
                    if selected_pump_id == 'All':
                        # Aggregate vibration data by timestamp
                        avg_vibration_over_time = vibration_data.groupby('Date').mean().reset_index()
                        fig = px.line(avg_vibration_over_time, x='Date', y='Vibration Level (mm/s)', title='Average Vibration Data Over Time')
                        fig.update_layout(width=550, height=300)
                        st.plotly_chart(fig)
                    else:
                        st.line_chart(vibration_data.set_index('Date')['Vibration Level (mm/s)'])

            #st.markdown('Estimated Remaining Useful Life (RUL) and Results')

            col3, col4 = st.columns([1, 2])

            with col3:
                st.subheader('***Estimated RUL***')
                if selected_pump_id == 'All':
                    # Calculate overall average RUL for all pumps
                    estimated_rul_percentage = mtbf_data['RUL (%)'].mean() if not mtbf_data.empty else 0
                else:
                    # Use the RUL of the selected pump
                    estimated_rul_percentage = mtbf_data['RUL (%)'].iloc[0] if not mtbf_data.empty else 0

                # Create gauge chart using Plotly
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=estimated_rul_percentage,
                    title={'text': "RUL Percentage"},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [
                               {'range': [0, 50], 'color': "lightgray"},
                               {'range': [50, 100], 'color': "gray"}]},
                    number={'suffix': '%', 'valueformat': '.2f'}))

                fig.update_layout(width=550, height=300)  # Adjust the size of the gauge
                st.plotly_chart(fig)

            with col4:
                st.subheader('***MTBF and RUL Results***')
                fig.update_layout(width=550, height=300)
                st.dataframe(mtbf_data)

        else:
            st.error('Required columns (PumpID) are missing in the uploaded files.')

    except Exception as e:
        st.error(f"Error: {e}")

# Display help text if no files are uploaded
if operating_data is None or vibration_data is None or maintenance_data is None:
    st.write("Please upload Operating Data, Vibration Data, and Maintenance History files to begin analysis.")
