import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import base64
import zipfile
from io import BytesIO

# Set page configuration
st.set_page_config(layout="wide")

# Function to download sample_data_formats.zip
def download_sample_data():
    sample_operating_data = pd.DataFrame({
        'PumpID': [1, 1, 2, 2],
        'Date': ['2024-06-01', '2024-06-02', '2024-06-01', '2024-06-02'],
        'Operating Hours': [8, 5, 4, 2]
    })

    sample_vibration_data = pd.DataFrame({
        'PumpID': [1, 1, 2, 2],
        'Date': ['2024-06-01 08:00:00', '2024-06-02 08:00:00', '2024-06-01 08:00:00', '2024-06-02 08:00:00'],
        'Vibration Level (mm/s)': [0.5, 0.6, 0.7, 0.8]
    })

    sample_maintenance_data = pd.DataFrame({
        'PumpID': [1, 1, 2, 2],
        'Failure Date': ['2024-06-01', '2024-06-02', '2024-06-01', '2024-06-02'],
        'Description': ['Change oil', 'Replace bearings', 'Clean filters', 'Inspect seals']
    })

    sample_equipment_data = pd.DataFrame({
        'PumpID': [1, 2, 3, 4],
        'ManufactureDate': ['2015-01-01', '2016-06-15', '2017-03-20', '2018-09-10'],
        'ExpireDate': ['2025-01-01', '2026-06-15', '2027-03-20', '2028-09-10']
    })

    zip_data = BytesIO()

    with zipfile.ZipFile(zip_data, mode='w') as zipf:
        for data, name in zip([sample_operating_data, sample_vibration_data, sample_maintenance_data, sample_equipment_data],
                              ['Sample_Operating_Data.xlsx', 'Sample_Vibration_Data.xlsx', 'Sample_Maintenance_Data.xlsx', 'Sample_Equipment_Data.xlsx']):
            excel_data = BytesIO()
            data.to_excel(excel_data, index=False)
            zipf.writestr(name, excel_data.getvalue())

    zip_data.seek(0)
    b64 = base64.b64encode(zip_data.read()).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="sample_data.zip">Download sample_data.zip</a>'
    return href

def calculate_mtbf(operating_data, maintenance_data):
    total_operating_time = operating_data.groupby('PumpID')['Operating Hours'].sum().reset_index()
    num_failures = maintenance_data.groupby('PumpID').size().reset_index(name='Number of Failures')
    mtbf_data = pd.merge(total_operating_time, num_failures, on='PumpID', how='outer')
    mtbf_data['MTBF (Hours)'] = mtbf_data['Operating Hours'] // mtbf_data['Number of Failures']
    return mtbf_data

def calculate_rul(mtbf_data, equipment_data):
    current_date = pd.to_datetime('now')
    equipment_data['ManufactureDate'] = pd.to_datetime(equipment_data['ManufactureDate'])
    equipment_data['ExpireDate'] = pd.to_datetime(equipment_data['ExpireDate'])
    equipment_data['Pump Age (Days)'] = (current_date - equipment_data['ManufactureDate']).dt.days

    if 'ExpireDate' in equipment_data.columns:
        equipment_data['Expected Lifespan (Days)'] = (equipment_data['ExpireDate'] - equipment_data['ManufactureDate']).dt.days
        mtbf_data = pd.merge(mtbf_data, equipment_data[['PumpID', 'Pump Age (Days)', 'Expected Lifespan (Days)']], on='PumpID', how='left')
        mtbf_data['RUL (%)'] = ((mtbf_data['Expected Lifespan (Days)'] - mtbf_data['Pump Age (Days)']) / mtbf_data['Expected Lifespan (Days)']) * 100
        mtbf_data['RUL (%)'] = mtbf_data['RUL (%)'].clip(lower=0)
        mtbf_data['RUL (%)'] = mtbf_data['RUL (%)'].round(2)
    else:
        st.error("Error: 'ExpireDate' column is missing in Equipment Data.")

    return mtbf_data

def main():
    st.title('Pump Maintenance and Performance Analyzer')

    # Description of the Pump Maintenance Calculator
    if 'show_description' not in st.session_state:
        st.session_state.show_description = False

    if not st.session_state.show_description:
        st.markdown("""
        The Pump Maintenance Calculator is designed to analyze and visualize pump performance and maintenance data. It provides insights into Mean Time Between Failures (MTBF) and estimates the Remaining Useful Life (RUL) of pumps based on historical data and sensor readings.

        ### How to Use:
        1. **Upload Data:** Upload your operating data, vibration data, maintenance history, and equipment data using the file uploader on the left.
        2. **View Data:** After uploading, review the data tables to ensure correctness.
        3. **Proceed to Visuals:** Click the "Proceed to Visuals" button to view visualizations and calculated metrics.

        **Sample Data Tables:** Below are sample tables for each type of data:
        """)
        st.session_state.show_description = True

    # Sample Data Tables
    if 'show_sample_data' not in st.session_state:
        st.session_state.show_sample_data = False

    if not st.session_state.show_sample_data:
        st.subheader('Sample Operating Data')
        sample_operating_data = pd.DataFrame({
            'PumpID': [1, 1, 2, 2],
            'Date': ['2024-06-01', '2024-06-02', '2024-06-01', '2024-06-02'],
            'Operating Hours': [8, 5, 4, 2]
        })
        st.dataframe(sample_operating_data)

        st.subheader('Sample Vibration Data')
        sample_vibration_data = pd.DataFrame({
            'PumpID': [1, 1, 2, 2],
            'Date': ['2024-06-01 08:00:00', '2024-06-02 08:00:00', '2024-06-01 08:00:00', '2024-06-02 08:00:00'],
            'Vibration Level (mm/s)': [0.5, 0.6, 0.7, 0.8]
        })
        st.dataframe(sample_vibration_data)

        st.subheader('Sample Maintenance History')
        sample_maintenance_data = pd.DataFrame({
            'PumpID': [1, 1, 2, 2],
            'Failure Date': ['2024-06-01', '2024-06-02', '2024-06-01', '2024-06-02'],
            'Description': ['Change oil', 'Replace bearings', 'Clean filters', 'Inspect seals']
        })
        st.dataframe(sample_maintenance_data)

        st.subheader('Sample Equipment Data')
        sample_equipment_data = pd.DataFrame({
            'PumpID': [1, 2, 3, 4],
            'ManufactureDate': ['2015-01-01', '2016-06-15', '2017-03-20', '2018-09-10'],
            'ExpireDate': ['2025-01-01', '2026-06-15', '2027-03-20', '2028-09-10']
        })
        st.dataframe(sample_equipment_data)

        st.session_state.show_sample_data = True

    if 'show_visuals' not in st.session_state:
        st.session_state.show_visuals = False

    if 'operating_data' not in st.session_state:
        st.session_state.operating_data = None

    if 'vibration_data' not in st.session_state:
        st.session_state.vibration_data = None

    if 'maintenance_data' not in st.session_state:
        st.session_state.maintenance_data = None

    if 'equipment_data' not in st.session_state:
        st.session_state.equipment_data = None

##- commented the following to disable runtime input/load of files

    #with st.sidebar.expander("Upload Data Files"):
     #  operating_file = st.file_uploader('Operating Data', type=['xlsx'])
     #  vibration_file = st.file_uploader('Vibration Data', type=['xlsx'])
     #  maintenance_file = st.file_uploader('Maintenance History', type=['xlsx'])
     #  equipment_file = st.file_uploader('Equipment Data', type=['xlsx'])

     #  st.markdown(download_sample_data(), unsafe_allow_html=True)

    #if operating_file:
    #    st.session_state.operating_data = pd.read_excel(operating_file)

    #if vibration_file:
    #    st.session_state.vibration_data = pd.read_excel(vibration_file)
    
    #if maintenance_file:
    #    st.session_state.maintenance_data = pd.read_excel(maintenance_file)
    
    #if equipment_file:
    #    st.session_state.equipment_data = pd.read_excel(equipment_file)

##- commented the above to disable runtime input/load of files

    if "c:\\temp\\Operating.xlsx" :
        st.session_state.operating_data = pd.read_excel("c:\\temp\\Operating.xlsx")

    if "c:\\temp\\Vibration.xlsx" :
        st.session_state.vibration_data = pd.read_excel("c:\\temp\\Vibration.xlsx")

    if "c:\\temp\\Maintenance.xlsx" :
        st.session_state.maintenance_data = pd.read_excel("c:\\temp\\Maintenance.xlsx")

    if "c:\\temp\\Equipment.xlsx" :
        st.session_state.equipment_data = pd.read_excel("c:\\temp\\Equipment.xlsx")

##- added the above code to static define input/load of files

   # if not st.session_state.show_visuals:
        if st.session_state.operating_data is not None:
            st.subheader('Operating Data')
            st.write(st.session_state.operating_data)

        if st.session_state.vibration_data is not None:
            st.subheader('Vibration Data')
            st.write(st.session_state.vibration_data)

        if st.session_state.maintenance_data is not None:
            st.subheader('Maintenance History')
            st.write(st.session_state.maintenance_data)

        if st.session_state.equipment_data is not None:
            st.subheader('Equipment Data')
            st.write(st.session_state.equipment_data)

    if st.button('Proceed to Visuals'):
       st.session_state.show_visuals = True

    if st.session_state.show_visuals:

        st.session_state.empty
        st.empty
        if st.session_state.operating_data is not None and st.session_state.vibration_data is not None and st.session_state.maintenance_data is not None and st.session_state.equipment_data is not None:
            operating_data = st.session_state.operating_data
            vibration_data = st.session_state.vibration_data
            maintenance_data = st.session_state.maintenance_data
            equipment_data = st.session_state.equipment_data

            mtbf_data = calculate_mtbf(operating_data, maintenance_data)
            mtbf_data = calculate_rul(mtbf_data, equipment_data)

            st.sidebar.subheader('Filter Data by RUL (%)')
            rul_percentage = st.sidebar.slider('Select RUL (%)', min_value=0, max_value=100, value=0)
            filtered_mtbf_data = mtbf_data[mtbf_data['RUL (%)'] >= rul_percentage]

            st.sidebar.header('Filter Results by Pump ID')
            pump_id_options = ['All'] + filtered_mtbf_data['PumpID'].unique().tolist()
            selected_pump_id = st.sidebar.selectbox('Select Pump ID', pump_id_options)

            if selected_pump_id != 'All':
                filtered_mtbf_data = filtered_mtbf_data[filtered_mtbf_data['PumpID'] == selected_pump_id]

            col1, col2 = st.columns([1, 1])

            with col1:
                if 'Date' in operating_data.columns:
                    filtered_operating_data = operating_data[operating_data['PumpID'].isin(filtered_mtbf_data['PumpID'])]
                    avg_operating_data = filtered_operating_data.groupby('Date')['Operating Hours'].mean().reset_index()
                    fig = px.line(avg_operating_data, x='Date', y='Operating Hours')
                    fig.update_layout(title='Average Operating Hours Over Time', xaxis_title='Date', yaxis_title='Operating Hours')
                    st.plotly_chart(fig)

            with col2:
                if 'Date' in vibration_data.columns:
                    filtered_vibration_data = vibration_data[vibration_data['PumpID'].isin(filtered_mtbf_data['PumpID'])]
                    avg_vibration_data = filtered_vibration_data.groupby('Date')['Vibration Level (mm/s)'].mean().reset_index()
                    fig = px.line(avg_vibration_data, x='Date', y='Vibration Level (mm/s)')
                    fig.update_layout(title='Average Vibration Levels Over Time', xaxis_title='Date', yaxis_title='Vibration Level (mm/s)')
                    st.plotly_chart(fig)

            col3, col4 = st.columns([1, 1])

            with col3:
                st.subheader('RUL Gauge')
                average_rul = filtered_mtbf_data['RUL (%)'].mean()
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=average_rul,
                    title={'text': "Average RUL (%)"}, 
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [
                               {'range': [0, 50], 'color': "lightgray"},
                               {'range': [50, 100], 'color': "gray"}]},
                    number={'suffix': '%', 'valueformat': '.2f'}))
                fig.update_layout(width=350, height=350)
                st.plotly_chart(fig)

            with col4:
                st.subheader('MTBF and RUL Data')
                st.dataframe(filtered_mtbf_data)

if __name__ == "__main__":
    main()
