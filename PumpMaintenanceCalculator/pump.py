import warnings 
warnings.simplefilter(action='ignore', category=FutureWarning)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # Ensure plotly.express is imported
import base64
import zipfile
from io import BytesIO
import numpy as np

# Set page configuration (call this only once at the beginning)
st.set_page_config(layout="wide")
st.markdown('<style>div.block-container { padding-top: 3rem; background-color: #E1FAF4; }</style>', unsafe_allow_html=True)

# Define session state keys
if 'upload_mode' not in st.session_state:
    st.session_state.upload_mode = False
if 'show_visuals' not in st.session_state:
    st.session_state.show_visuals = False

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {
        'operating_data': None,
        'vibration_data': None,
        'maintenance_data': None,
        'equipment_data': None
    }

def download_sample_data():
    # Function to download sample_data_formats.zip
    sample_operating_data = pd.DataFrame({
        'PumpID': [1, 1, 2, 2],
        'Date': ['01-06-2024', '02-06-2024', '03-06-2024', '04-06-2024'],
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
        'ManufactureDate': ['2005-01-01', '2016-06-15', '2017-03-20', '2018-09-10'],
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
    href = f'<a href="data:application/zip;base64,{b64}" download="sample_data.zip">Click Here</a>'
    return href

def calculate_mtbf(operating_data, maintenance_data):
    # Function to calculate MTBF
    total_operating_time = operating_data.groupby('PumpID')['Operating Hours'].sum().reset_index()
    num_failures = maintenance_data.groupby('PumpID').size().reset_index(name='Number of Failures')
    mtbf_data = pd.merge(total_operating_time, num_failures, on='PumpID', how='outer')
    mtbf_data['MTBF (Hours)'] = mtbf_data['Operating Hours'] // mtbf_data['Number of Failures']
    return mtbf_data

def calculate_rul(mtbf_data, equipment_data):
    # Function to calculate RUL
    current_date = pd.Timestamp.now()
    equipment_data['ManufactureDate'] = pd.to_datetime(equipment_data['ManufactureDate'])
    equipment_data['ExpireDate'] = pd.to_datetime(equipment_data['ExpireDate'])
    equipment_data['Pump Age (Days)'] = (current_date - equipment_data['ManufactureDate']).dt.days

    if 'ExpireDate' in equipment_data.columns:
        equipment_data['Expected Lifespan (Days)'] = (equipment_data['ExpireDate'] - equipment_data['ManufactureDate']).dt.days
        mtbf_data = pd.merge(mtbf_data, equipment_data[['PumpID', 'Pump Age (Days)', 'Expected Lifespan (Days)']], on='PumpID', how='left')
        mtbf_data['RUL (%)'] = ((mtbf_data['Expected Lifespan (Days)'] - mtbf_data['Pump Age (Days)']) / mtbf_data['Expected Lifespan (Days)']) * 100
        mtbf_data['RUL (%)'] = mtbf_data['RUL (%)'].clip(lower=0)
        mtbf_data['RUL (%)'] = np.array(mtbf_data['RUL (%)']).round(2)
    else:
        st.error("Error: 'ExpireDate' column is missing in Equipment Data.")

    return mtbf_data

def main():

    st.markdown("<h2 style='text-align: center; color: green;'>Pump Maintenance and Performance Analyzer</h2>", unsafe_allow_html=True) 

    if st.session_state.upload_mode:
        # File upload mode
        with st.sidebar.expander("Please upload all required custom data files."): 

            operating_file = st.file_uploader("Operating Data", type=["xlsx"])
            vibration_file = st.file_uploader("Vibration Data", type=["xlsx"])
            maintenance_file = st.file_uploader("Maintenance History", type=["xlsx"])
            equipment_file = st.file_uploader("Equipment Data", type=["xlsx"])

            if operating_file:
                st.session_state.uploaded_files['operating_data'] = operating_file
            if vibration_file:
                st.session_state.uploaded_files['vibration_data'] = vibration_file
            if maintenance_file:
                st.session_state.uploaded_files['maintenance_data'] = maintenance_file
            if equipment_file:
                st.session_state.uploaded_files['equipment_data'] = equipment_file

        uploaded_files = st.session_state.uploaded_files

        if all(uploaded_files.values()):
            operating_data = pd.read_excel(uploaded_files['operating_data'])
            vibration_data = pd.read_excel(uploaded_files['vibration_data'])
            maintenance_data = pd.read_excel(uploaded_files['maintenance_data'])
            equipment_data = pd.read_excel(uploaded_files['equipment_data'])

            #st.header('Uploaded Data')
            st.markdown("<h4 style='text-align: center; color: blue;'>[[Custom Data]]</h4>", unsafe_allow_html=True) 
            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Operating Data')
                st.dataframe(operating_data)

                st.subheader('Vibration Data')
                st.dataframe(vibration_data)

            with col2:
                st.subheader('Maintenance History')
                st.dataframe(maintenance_data)

                st.subheader('Equipment Data')
                st.dataframe(equipment_data)

            st.markdown("<h2 style='text-align: center; color: black;'>Visuals genetated with Custom data</h2>", unsafe_allow_html=True)
            sidebar_fraction = 0.3  # Adjust the fraction as needed, e.g., 0.3 means 30% of the total width

            # Layout using st.sidebar and st
            st.subheader('Filter Data by RUL (%)and PumpID')

            # Use st for the main content area
            col1, col2 = st.columns([sidebar_fraction, 1 - sidebar_fraction])  # Adjust as needed
            with col1:
                rul_percentage = st.slider('Select RUL (%)', min_value=0, max_value=100, value=0)

            # Calculate MTBF and RUL based on uploaded data
            mtbf_data = calculate_mtbf(operating_data, maintenance_data)
            mtbf_data = calculate_rul(mtbf_data, equipment_data)

            filtered_mtbf_data = mtbf_data[mtbf_data['RUL (%)'] >= rul_percentage]

            #st.header('Filter by Pump ID')

            with col1:
                pump_id_options = ['All'] + filtered_mtbf_data['PumpID'].unique().tolist()
                selected_pump_id = st.selectbox('Select Pump ID', pump_id_options)

            if selected_pump_id != 'All':
                filtered_mtbf_data = filtered_mtbf_data[filtered_mtbf_data['PumpID'] == selected_pump_id]
                filtered_operating_data = operating_data[operating_data['PumpID'] == selected_pump_id]

            # Narrative section
            if selected_pump_id == 'All':
                st.markdown("""
                ### Overall Pump Performance Overview:
                - The average <span style='color: blue;'>Operating Hours</span> across all pumps is <span style='color: blue; font-weight: bold;'>{:.2f} hours</span>.
                - The average <span style='color: blue;'>RUL (%)</span> across all pumps is <span style='color: blue; font-weight: bold;'>{:.2f}%</span>.
                """.format(operating_data['Operating Hours'].mean(), filtered_mtbf_data['RUL (%)'].mean()), unsafe_allow_html=True)
            else:
                st.markdown("""
                ### Performance Overview for Pump ID {}:
                - For Pump ID <span style='color: blue;'>{}</span>, the average <span style='color: blue;'>Operating Hours</span> is <span style='color: blue; font-weight: bold;'>{:.2f} hours</span>.
                - The average <span style='color: blue;'>RUL (%)</span> is <span style='color: blue; font-weight: bold;'>{:.2f}%</span>.
                """.format(selected_pump_id, selected_pump_id, filtered_operating_data['Operating Hours'].mean(), filtered_mtbf_data['RUL (%)'].mean()), unsafe_allow_html=True)

            # Visualizations based on uploaded data
            col1, col2 = st.columns([1, 1])

            with col1:
                if 'Date' in operating_data.columns:
                    st.subheader('Average MTBF Over Time')
                    filtered_operating_data = operating_data[operating_data['PumpID'].isin(filtered_mtbf_data['PumpID'])]
                    avg_operating_data = filtered_operating_data.groupby('Date')['Operating Hours'].mean().reset_index()
                    fig = px.line(avg_operating_data, x='Date', y='Operating Hours')
                    fig.update_layout(title='', xaxis_title='Date', yaxis_title='Operating Hours')
                    st.plotly_chart(fig)

            with col2:
                if 'Date' in vibration_data.columns:
                    st.subheader('Average Vibration Levels Over Time')
                    filtered_vibration_data = vibration_data[vibration_data['PumpID'].isin(filtered_mtbf_data['PumpID'])]
                    avg_vibration_data = filtered_vibration_data.groupby('Date')['Vibration Level (mm/s)'].mean().reset_index()
                    fig = px.line(avg_vibration_data, x='Date', y='Vibration Level (mm/s)')
                    fig.update_layout(title='', xaxis_title='Date', yaxis_title='Vibration Level (mm/s)')
                    st.plotly_chart(fig)

            col3, col4 = st.columns([1, 1])

            with col3:
                st.subheader('Estimated RUL (%)')
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
                st.subheader('Estimated RUL Details')
                st.dataframe(filtered_mtbf_data.drop(columns=['Operating Hours', 'Number of Failures', 'MTBF (Hours)']))

        else:
            st.warning('Please upload all required custom data files.')

    else:
        # Description of the Pump Maintenance Calculator
        download_link = download_sample_data()

        st.markdown(f""" 
            The **Pump Maintenance Calculator** helps visualize pump performance and maintenance with insights into Mean Time Between Failures (**MTBF**) and Remaining Useful Life (**RUL**). The input datasets and output visuals are as explained below:\n
            **Input**:  
            1. Equipment/Pump data : list of equipment or pump information having Pump ID, Date of Mfg, Date of Expiry\n
            2. Pump Operations dataset consisting of : Pump ID, Date of operation, and Hours of operation \n
            3. Pump Maintenance History consisting of : Pump ID, Date of Failure, Maintenance Done \n
            4. Pump Vibrations dataset (collected via sensors) : Pump ID, Date/Time, Vibration Level (mm/sec)\n  
            **Output**:\n
            1. Trend showing MTBF and Vibrations  \n
            2. RUL guage and detail     \n
            """, unsafe_allow_html=True)

        st.markdown("<h4 style='text-align: center; color: black;'>Sample datasets</h4>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col2:
            st.subheader('Pump Operations')
            sample_operating_data = pd.DataFrame({
                'PumpID': [1, 1, 2, 2],
                'Date': ['2024-06-01', '2024-06-02', '2024-06-03', '2024-06-04'],
                'Operating Hours': [8, 5, 4, 2]
            })
            st.dataframe(sample_operating_data)

            st.subheader('Pump Vibrations')
            sample_vibration_data = pd.DataFrame({
                'PumpID': [1, 1, 2, 2],
                'Date': ['2024-06-01 08:00:00', '2024-06-02 08:00:00', '2024-06-01 08:00:00', '2024-06-02 08:00:00'],
                'Vibration Level (mm/s)': [0.5, 0.6, 0.7, 0.8]
            })
            st.dataframe(sample_vibration_data)

        with col1:
            st.subheader('Equipment/Pumps')
            sample_equipment_data = pd.DataFrame({
                'PumpID': [1, 2, 3, 4],
                'ManufactureDate': ['2005-01-01', '2016-06-15', '1939-12-30', '1940-11-04'],
                'ExpireDate': ['2025-01-01', '2026-06-15', '1998-04-05','2001-12-15']
            })
            st.dataframe(sample_equipment_data)

            st.subheader('Pump Maintenance History')
            sample_maintenance_data = pd.DataFrame({
                'PumpID': [1, 1, 2, 2],
                'Failure Date': ['2024-06-01', '2024-06-02', '2024-06-01', '2024-06-02'],
                'Description': ['Change oil', 'Replace bearings', 'Clean filters', 'Inspect seals']
            })
            st.dataframe(sample_maintenance_data)
        if st.button('Generate Visuals with above Sample data'):
                st.session_state.show_visuals = True
                st.session_state.upload_mode = False

        if st.session_state.show_visuals:
            st.markdown("<h3 style='text-align: center; color: Blue;'>Visuals genetated from above sample data</h3>", unsafe_allow_html=True)

            st.subheader("Filter Data by RUL (%) and PumpID")

            col1, col2 = st.columns([1, 3])  # Adjust as needed
            with col1:
                rul_percentage = st.slider('Select RUL (%)', min_value=0, max_value=100, value=0)

            # Calculate MTBF and RUL based on sample data
            mtbf_data = calculate_mtbf(sample_operating_data, sample_maintenance_data)
            mtbf_data = calculate_rul(mtbf_data, sample_equipment_data)

            filtered_mtbf_data = mtbf_data[mtbf_data['RUL (%)'] >= rul_percentage]
            col1, col2 = st.columns([1, 3])
            with col1:
                #st.header('***Filter Results by Pump ID***')
                pump_id_options = ['All'] + filtered_mtbf_data['PumpID'].unique().tolist()
                selected_pump_id = st.selectbox('Select Pump ID', pump_id_options)

            if selected_pump_id != 'All':
                filtered_mtbf_data = filtered_mtbf_data[filtered_mtbf_data['PumpID'] == selected_pump_id]
                filtered_operating_data = sample_operating_data[sample_operating_data['PumpID'] == selected_pump_id]


            # Generate visuals based on filtered sample data
            col1, col2 = st.columns([1, 1])

            with col1:
                if 'Date' in sample_operating_data.columns:
                    st.subheader('Average MTBF Over Time')
                    if 'PumpID' in filtered_mtbf_data.columns:
                        filtered_operating_data = sample_operating_data[sample_operating_data['PumpID'].isin(filtered_mtbf_data['PumpID'])]
                    avg_operating_data = filtered_operating_data.groupby('Date')['Operating Hours'].mean().reset_index()
                    fig = px.line(avg_operating_data, x='Date', y='Operating Hours')
                    fig.update_layout(title='', xaxis_title='Date', yaxis_title='Operating Hours')
                    st.plotly_chart(fig)

            with col2:
                if 'Date' in sample_vibration_data.columns:
                    st.subheader('Average Vibration Levels Over Time')
                    if 'PumpID' in filtered_mtbf_data.columns:
                        filtered_vibration_data = sample_vibration_data[sample_vibration_data['PumpID'].isin(filtered_mtbf_data['PumpID'])]
                    avg_vibration_data = filtered_vibration_data.groupby('Date')['Vibration Level (mm/s)'].mean().reset_index()
                    fig = px.line(avg_vibration_data, x='Date', y='Vibration Level (mm/s)')
                    fig.update_layout(title='', xaxis_title='Date', yaxis_title='Vibration Level (mm/s)')
                    st.plotly_chart(fig)

            col3, col4 = st.columns([1, 1])

            with col3:
                st.subheader('Estimated RUL (%)')
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
                st.subheader('Estimated RUL Details')
                st.dataframe(filtered_mtbf_data.drop(columns=['Operating Hours', 'Number of Failures', 'MTBF (Hours)']))

            st.markdown(f"""<h4>Want to try with custom data</h4>
              [({download_link}) to download excel templates with sample data. You may add/modify data into each of the excel template, save and upload to view the visuals per the uploaded custom data]""", unsafe_allow_html=True) 

    #if st.button('Show Visuals'):
        #st.session_state.show_visuals = True
        #st.session_state.upload_mode = False  # Ensure upload mode is off initially

    # Enter Upload Mode button (only show if Show Visuals button was clicked)
    if st.session_state.show_visuals:
        if st.button('Upload custom data files'):
            st.session_state.upload_mode = True
            st.session_state.show_visuals = False
            st.rerun()    # Turn off show visuals after entering upload mode
    

if __name__ == '__main__':
    main()