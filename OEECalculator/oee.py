import streamlit as st 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import base64
import zipfile
from io import BytesIO

# Set page configuration 
st.set_page_config(layout="wide")
st.markdown('<style>div.block-container { padding-top: 3rem; background-color: #E3F4F4; }</style>', unsafe_allow_html=True)


# Define session state keys
if 'upload_mode' not in st.session_state:
    st.session_state.upload_mode = False
if 'visuals_generated' not in st.session_state:
    st.session_state.visuals_generated = False

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {
        'production_hours_data': None,
        'downtime_hours_data': None
    }

def download_sample_data():
    # Sample Production Hours Data
    sample_production_hours_data = pd.DataFrame({
        'Date': ['2024-06-15', '2024-06-15', '2024-06-15', '2024-06-16', '2024-06-16', '2024-06-16'],
        'EquipmentId': [11, 12, 13, 11, 12, 13],
        'ProductionHrs': [21, 19, 17, 22, 11, 17],
        'ProducedGoods': [817, 563, 550, 977, 470, 523],
        'DefectGoods': [42, 50, 38, 39, 27, 38],
        'IdealCycle': [1.4, 1.6, 1.5, 1.3, 1.2, 1.5]
    })

    # Sample Downtime Hours Data
    sample_downtime_hours_data = pd.DataFrame({
        'Date': ['2024-06-15', '2024-06-15', '2024-06-15', '2024-06-16', '2024-06-16', '2024-06-16'],
        'EquipmentId': [11, 12, 13, 11, 12, 13],
        'DownTimeHrs': [1.1, 1.3, 1.5, 0.8, 1.2, 1.0]
    })

    zip_data = BytesIO()

    with zipfile.ZipFile(zip_data, mode='w') as zipf:
        for data, name in zip([sample_production_hours_data, sample_downtime_hours_data],
                              ['Sample_Production_Hours_Data.xlsx', 'Sample_Downtime_Hours_Data.xlsx']):
            excel_data = BytesIO()
            data.to_excel(excel_data, index=False)
            zipf.writestr(name, excel_data.getvalue())

    zip_data.seek(0)
    b64 = base64.b64encode(zip_data.read()).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="sample_data_oee.zip">Click here</a>'
    return href

def calculate_oee(production_hours_data, downtime_hours_data):
    # Merge production and downtime data
    merged_data = pd.merge(production_hours_data, downtime_hours_data, on=['Date', 'EquipmentId'])

    # Calculate OEE Components
    merged_data['Availability'] = (merged_data['ProductionHrs'] - merged_data['DownTimeHrs']) / merged_data['ProductionHrs']
    merged_data['Performance'] = (merged_data['ProducedGoods'] * merged_data['IdealCycle']) / ((merged_data['ProductionHrs'] - merged_data['DownTimeHrs']) * 60)
    merged_data['Quality'] = (merged_data['ProducedGoods'] - merged_data['DefectGoods']) / merged_data['ProducedGoods']
    merged_data['OEE'] = merged_data['Availability'] * merged_data['Performance'] * merged_data['Quality'] * 100
    return merged_data

# Function for sample mode
def sample_mode():
    download_link = download_sample_data()
    st.title('🔢:blue[Overall Equipment Effectiveness (OEE) Calculator]')
    st.markdown(f"""
        The **Overall Equipment Effectiveness (OEE)** calculator measures the efficiency and productivity of equipment. The input datasets and output visuals are as explained below:\n
        **Input** : \n
        1. Production dataset consisting of : Date of production, Equipment ID, Hours of Operation, Units of Goods produced, Count of Defective products, Time to produce one unit.\n
        2. Equipment Downtime dataset consisting of : Date of downtime, Equipment ID, Downtime in Hours, Downtime Reason.\n
        **Output** :\n
        Percent of, equipment  **Availability**⏱️, its **Performance**⚙️, produce **Quality**✔️ and finally its **OEE**.\n
        **Sample Input datasets**:
    """, unsafe_allow_html=True)

    # Sample Data Tables
    sample_production_hours_data = pd.DataFrame({
        'Date': ['2024-06-15', '2024-06-15', '2024-06-15', '2024-06-16', '2024-06-16', '2024-06-16'],
        'EquipmentId': [11, 12, 13, 11, 12, 13],
        'ProductionHrs': [21, 19, 17, 22, 11, 17],
        'ProducedGoods': [817, 563, 550, 977, 470, 523],
        'DefectGoods': [42, 50, 38, 39, 27, 38],
        'IdealCycle': [1.4, 1.6, 1.5, 1.3, 1.2, 1.5]
    })

    sample_downtime_hours_data = pd.DataFrame({
        'Date': ['2024-06-15', '2024-06-15', '2024-06-15', '2024-06-16', '2024-06-16', '2024-06-16'],
        'EquipmentId': [11, 12, 13, 11, 12, 13],
        'DownTimeHrs': [1.1, 1.3, 1.5, 0.8, 1.2, 1.0]
    })

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(sample_production_hours_data, height=250, use_container_width=True,hide_index=True)

    with col2:
        st.dataframe(sample_downtime_hours_data, height=250, use_container_width=True, hide_index=True)

    if st.button("Generate Visuals using Sample Data"):
        st.session_state.visuals_generated = True
        st.session_state.upload_mode = False

    if st.session_state.visuals_generated:
        merged_data = pd.merge(sample_production_hours_data, sample_downtime_hours_data, on=['Date', 'EquipmentId'])

        merged_data['Availability'] = (merged_data['ProductionHrs'] - merged_data['DownTimeHrs']) / merged_data['ProductionHrs']
        merged_data['Performance'] = (merged_data['ProducedGoods'] * merged_data['IdealCycle']) / ((merged_data['ProductionHrs'] - merged_data['DownTimeHrs']) * 60)
        merged_data['Quality'] = (merged_data['ProducedGoods'] - merged_data['DefectGoods']) / merged_data['ProducedGoods']
        merged_data['OEE'] = merged_data['Availability'] * merged_data['Performance'] * merged_data['Quality'] * 100

        # Filter results by ID
        st.markdown("<h2 style='text-align: center; color: #0768C9;'>Visuals Generated from Sample Data </h2>", unsafe_allow_html=True)
        col1,col2,col3=st.columns(3)
        with col1:
          available_ids = merged_data['EquipmentId'].unique().tolist()
          selected_id = st.selectbox('**Filter Results by Equipment ID**', ['All'] + available_ids)

        if selected_id != 'All':
            filtered_data = merged_data[merged_data['EquipmentId'] == selected_id]
        else:
            filtered_data = merged_data

        # Calculate averages
        average_availability = filtered_data['Availability'].mean()
        average_performance = filtered_data['Performance'].mean()
        average_quality = filtered_data['Quality'].mean()
        average_oee = (average_availability * average_performance * average_quality) * 100

        avg_oee_date_data = filtered_data.groupby('Date')['OEE'].mean().reset_index()
        fig_oee_over_time = px.line(avg_oee_date_data, x='Date', y='OEE', title='Average OEE of Equipment on Each Date', height=350)

        avg_metrics_data = filtered_data.groupby('EquipmentId')[['Availability', 'Performance', 'Quality']].mean().reset_index()
        avg_metrics_data = avg_metrics_data.melt(id_vars=['EquipmentId'], value_vars=['Availability', 'Performance', 'Quality'],
                                                 var_name='Metric', value_name='Average')

        fig_avg_metrics = px.bar(avg_metrics_data, x='EquipmentId', y='Average', color='Metric', barmode='group',
                                 title='Average Availability, Performance, and Quality of Each Equipment',
                                 labels={'EquipmentId': 'Equipment ID', 'Average': 'Average Value'},
                                 hover_data={'Average': True},
                                 height=350)
        fig_avg_metrics.update_traces(texttemplate='%{y:.2%}')

        fig_availability = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_availability * 100,
            title={'text': "Average Availability"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#2779B7"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 100], 'color': "lightgray"}]},
            number={'suffix': '%', 'valueformat': '.2f'}))
        fig_availability.update_layout(width=500, height=330)

        fig_performance = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_performance * 100,
            title={'text': "Average Performance"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#83C9FF"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 100], 'color': "lightgray"}]},
            number={'suffix': '%', 'valueformat': '.2f'}))
        fig_performance.update_layout(width=500, height=330)

        fig_quality = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_quality * 100,
            title={'text': "Average Quality"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#FF2B2B"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 100], 'color': "lightgray"}]},
            number={'suffix': '%', 'valueformat': '.2f'}))
        fig_quality.update_layout(width=500, height=330)

        fig_oee = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_oee,
            title={'text': "Average OEE"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#FFABAB"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 100], 'color': "lightgray"}]},
            number={'suffix': '%', 'valueformat': '.2f'}))
        fig_oee.update_layout(width=500, height=330)

         # Calculate average OEE for each equipment ID
        avg_oee_data = filtered_data.groupby('EquipmentId')['OEE'].mean().reset_index()
        avg_oee_data.columns = ['EquipmentId', 'Average OEE']
        avg_oee_data['Average OEE'] = avg_oee_data['Average OEE'].apply(lambda x: f"{x :.2f}%")
             
        # Display results for each record in a table
        filtered_data_display = filtered_data[['Date', 'EquipmentId', 'Availability', 'Performance', 'Quality', 'OEE']]
        filtered_data_display.loc[:, 'Availability'] = filtered_data_display['Availability'].round(4)*100
        filtered_data_display.loc[:, 'Performance'] = filtered_data_display['Performance'].round(4)*100
        filtered_data_display.loc[:,'Quality'] = filtered_data_display['Quality'].round(4)*100  
        filtered_data_display.loc[:,'OEE'] = filtered_data_display['OEE'].round(2)

        if selected_id == 'All':
                  
                   # Display summary of metrics as text
                    st.markdown("**Summary**")
                    st.markdown(
                     f"""
                     <div style="color: blue;">
                    For Equipment IDs   <strong>{selected_id}</strong> ,
                    the Average Availability is  <strong>{average_availability:.2%}</strong> ,
                    the Average Performance is  <strong>{average_performance:.2%}</strong> ,
                    the Average Quality is  <strong>{average_quality:.2%}</strong> ,
                    and the Average OEE is  <strong>{average_oee/100:.2%}</strong>.</div>""", unsafe_allow_html=True)
        else:
                   
                   # Display summary of metrics as text
                    st.markdown("**Summary**")
                    st.markdown(f""" <div style="color: blue;">
                    For Equipment ID   <strong>{selected_id}</strong> ,
                    the Average Availability is  <strong>{average_availability:.2%}</strong> ,
                    the Average Performance is  <strong>{average_performance:.2%}</strong> ,
                    the Average Quality is  <strong>{average_quality :.2%}</strong> ,
                    and the Average OEE is  <strong>{average_oee/100:.2%}</strong>.
                   </div>
               """, unsafe_allow_html=True)

            # Display gauge charts for average metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
                st.plotly_chart(fig_availability)
        with col2:
                st.plotly_chart(fig_performance)
        with col3:
                st.plotly_chart(fig_quality)
        with col4:
                st.plotly_chart(fig_oee)

        col5,col6=st.columns(2)
        with col5:
                st.plotly_chart(fig_oee_over_time,use_container_width=True)
        with col6:
                st.plotly_chart(fig_avg_metrics,use_container_width=True)

        col7,col8=st.columns(2)
        with col7:
                st.write("**Equipment Metric Percentage Details**")
                
                st.dataframe(filtered_data_display,height=280,use_container_width=True, hide_index=True)
        with col8:
                st.write("**Average OEE of Each Equipment**")
                st.dataframe(avg_oee_data,height=280,use_container_width=True, hide_index=True)

        st.markdown(f"""<h4>Want to try with custom data</h4>
            [({download_link}) to download excel templates with sample data. You may add/modify data into each of the excel template, save and upload to view the visuals as per the uploaded custom data]""", unsafe_allow_html=True) 

    if st.session_state.visuals_generated:
       if st.button("Upload Custom data files"):
           st.session_state.upload_mode = True
           st.session_state.visuals_generated = False
           st.rerun()

# Function for upload mode
def upload_mode():
    st.title('🔢:blue[Overall Equipment Effectiveness (OEE) Calculator]')

    with st.sidebar.expander("Upload Custom data Files"):
      production_file = st.file_uploader("Upload Production Data", type=["csv", "xlsx"])
      downtime_file = st.file_uploader("Upload Downtime Data", type=["csv", "xlsx"])

    if production_file is not None and downtime_file is not None:
        if production_file.name.endswith('.csv'):
            production_data = pd.read_csv(production_file)
            
        else:
            production_data = pd.read_excel(production_file)
            

        if downtime_file.name.endswith('.csv'):
            downtime_data = pd.read_csv(downtime_file)
           
        else:
            downtime_data = pd.read_excel(downtime_file)
                    
        col1,col2=st.columns(2)
        with col1:
            st.write("**Uploaded Production Hours Data**")
            st.dataframe(production_data, height=250, use_container_width=True,hide_index=True)
        with col2:
            st.write("**Uploaded Downtime Hours Data**")
            st.dataframe(downtime_data, height=250, use_container_width=True,hide_index=True)

 
        merged_data = calculate_oee(production_data, downtime_data)

        # Filter results by ID
        st.markdown("<h2 style='text-align: center; color: #0768C9;'>Visuals Generated from Custom Data </h2>", unsafe_allow_html=True)
        col1,col2,col3=st.columns(3)
        with col1:
          #st.write('Filter Results by ID')
          available_ids = merged_data['EquipmentId'].unique().tolist()
          selected_id = st.selectbox('**Filter Results by Equipment ID**', ['All'] + available_ids)

        if selected_id != 'All':
            filtered_data = merged_data[merged_data['EquipmentId'] == selected_id]
        else:
            filtered_data = merged_data

        # Calculate averages
        average_availability = filtered_data['Availability'].mean()
        average_performance = filtered_data['Performance'].mean()
        average_quality = filtered_data['Quality'].mean()
        average_oee = (average_availability * average_performance * average_quality) * 100

        avg_oee_date_data = filtered_data.groupby('Date')['OEE'].mean().reset_index()
        fig_oee_over_time = px.line(avg_oee_date_data, x='Date', y='OEE', title='Average OEE of Equipment on Each Date', height=350)

        avg_metrics_data = filtered_data.groupby('EquipmentId')[['Availability', 'Performance', 'Quality']].mean().reset_index()
        avg_metrics_data = avg_metrics_data.melt(id_vars=['EquipmentId'], value_vars=['Availability', 'Performance', 'Quality'],
                                                 var_name='Metric', value_name='Average')

        fig_avg_metrics = px.bar(avg_metrics_data, x='EquipmentId', y='Average', color='Metric', barmode='group',
                                 title='Average Availability, Performance, and Quality of Each Equipment',
                                 labels={'EquipmentId': 'Equipment ID', 'Average': 'Average Value'},
                                 hover_data={'Average': True},
                                 height=350)
        fig_avg_metrics.update_traces(texttemplate='%{y:.2%}')

        fig_availability = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_availability * 100,
            title={'text': "Average Availability"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#2779B7"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 100], 'color': "lightgray"}]},
            number={'suffix': '%', 'valueformat': '.2f'}))
        fig_availability.update_layout(width=500, height=330)

        fig_performance = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_performance * 100,
            title={'text': "Average Performance"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#83C9FF"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 100], 'color': "lightgray"}]},
            number={'suffix': '%', 'valueformat': '.2f'}))
        fig_performance.update_layout(width=500, height=330)

        fig_quality = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_quality * 100,
            title={'text': "Average Quality"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#FF2B2B"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 100], 'color': "lightgray"}]},
            number={'suffix': '%', 'valueformat': '.2f'}))
        fig_quality.update_layout(width=500, height=330)

        fig_oee = go.Figure(go.Indicator(
            mode="gauge+number",
            value=average_oee,
            title={'text': "Average OEE"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#FFABAB"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 100], 'color': "lightgray"}]},
            number={'suffix': '%', 'valueformat': '.2f'}))
        fig_oee.update_layout(width=500, height=330)

        avg_oee_data = filtered_data.groupby('EquipmentId')['OEE'].mean().reset_index()
        avg_oee_data.columns = ['EquipmentId', 'Average OEE']
        avg_oee_data['Average OEE'] = avg_oee_data['Average OEE'].apply(lambda x: f"{x :.2f}%")
             
        # Display results for each record in a table
        filtered_data_display = filtered_data[['Date', 'EquipmentId', 'Availability', 'Performance', 'Quality', 'OEE']]
        filtered_data_display.loc[:, 'Availability'] = filtered_data_display['Availability'].round(4)*100 
        filtered_data_display.loc[:,'Performance'] = filtered_data_display['Performance'].round(4)*100 
        filtered_data_display.loc[:,'Quality'] = filtered_data_display['Quality'].round(4)*100 
        filtered_data_display.loc[:,'OEE'] = filtered_data_display['OEE'].round(2)
       
        if selected_id == 'All':
               
                    st.markdown("**Summary**")
                    st.markdown(
                     f"""
                     <div style="color: blue;">
                    For Equipment IDs   <strong>{selected_id}</strong> ,
                    the Average Availability is  <strong>{average_availability:.2%}</strong> ,
                    the Average Performance is  <strong>{average_performance:.2%}</strong> ,
                    the Average Quality is  <strong>{average_quality:.2%}</strong> ,
                    and the Average OEE is  <strong>{average_oee/100:.2%}</strong>.</div>""", unsafe_allow_html=True)
        else:
                   
                    st.markdown("**Summary**")
                    st.markdown(f""" <div style="color: blue;">
                    For Equipment ID   <strong>{selected_id}</strong> ,
                    the Average Availability is  <strong>{average_availability:.2%}</strong> ,
                    the Average Performance is  <strong>{average_performance:.2%}</strong> ,
                    the Average Quality is  <strong>{average_quality :.2%}</strong> ,
                    and the Average OEE is  <strong>{average_oee/100:.2%}</strong>.
                   </div>
               """, unsafe_allow_html=True)

            # Display gauge charts for average metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
                st.plotly_chart(fig_availability)
        with col2:
                st.plotly_chart(fig_performance)
        with col3:
                st.plotly_chart(fig_quality)
        with col4:
                st.plotly_chart(fig_oee)

        col5,col6=st.columns(2)
        with col5:
                st.plotly_chart(fig_oee_over_time,use_container_width=True)
        with col6:
                st.plotly_chart(fig_avg_metrics,use_container_width=True)

        col7,col8=st.columns(2)
        with col7:
                st.write("**Equipment Metric Percentage Details**")
                st.dataframe(filtered_data_display,height=280,use_container_width=True,hide_index=True)
        with col8:
                st.write("**Average OEE of Each Equipment**")
                st.dataframe(avg_oee_data,height=280,use_container_width=True, hide_index=True)


# Main logic to switch between modes
if st.session_state.upload_mode:
    upload_mode()
else:
    sample_mode()