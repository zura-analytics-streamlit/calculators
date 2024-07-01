import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import io

# Title of the app
st.set_page_config(page_title="OEE Calculator", page_icon="🔢", layout="wide")
st.title("🔢 OEE Calculator")
#st.markdown('<style>div.block-container{padding-top:3rem;background-color:"#98A1EC";}</style>', unsafe_allow_html=True)
st.markdown('<style>div.block-container { padding-top: 3rem; background-color: #ECFBF5; }</style>', unsafe_allow_html=True)
#st.markdown("""<style>.st-emotion-cache-ocqkz7.e1f1d6gn5{ background-color: #98A1EC; }</style>""", unsafe_allow_html=True)


#st.markdown("""<style>.stApp stAppEmbeddingId-sfxok0zvdhzr streamlit-wide st-emotion-cache-nq7g5c erw9t6i1 {background-color:"#98A1EC";} </style>""", unsafe_allow_html=True)

# Sample data integration (for testing purposes)
def download_sample_data():
  sample_production_data = """
    Instructions:
   ❗Please make sure that you are using one of the naming format for column names in your uploaded file - Date, date, production_date
   ❗Please make sure that you are using one of the naming format for column names in your uploaded file -Id: Id,id,machine_id,equipment_id
   ❗ Please make sure that you are using one of the naming formats for column names in your uploaded file - ProductionHrs: ProductionHrs, production_hours, prod_hours, Production Hours, ProductionHours
   ❗ Please make sure that you are using one of the naming formats for column names in your uploaded file -IdealCycle: IdealCycle,ideal_cycle_time, ideal_cycle
   ❗ Please make sure that you are using one of the naming formats for column names in your uploaded file - DownTimeHrs: DownTimeHrs, downtime_hours, down_hours

---Production Data JSON Sample----
[
    {
        "Date": "2023-06-21",
        "Id": 1,
        "ProductionHours": 8,
        "ProducedGoods": 1000,
        "DefectGoods": 50,
        "IdealCycle": 0.5
    },
    {
        "Date": "2023-06-22",
        "Id": 2,
        "ProductionHours": 7.5,
        "ProducedGoods": 950,
        "DefectGoods": 30,
        "IdealCycle": 0.55
    },
    {
        "Date": "2023-06-23",
        "Id": 3,
        "ProductionHours": 9,
        "ProducedGoods": 1100,
        "DefectGoods": 70,
        "IdealCycle": 0.6
    }]

-------Production hours Excel Sample-----
ID|Date    |Production Hours|Production Goods|Defect Goods|Ideal Cycle
1|2024-06-01 08:00:00|5|250|50|1.2
1|2024-06-02 08:00:00|6|258|60|1.5
2|2024-06-01 08:00:00|7|270|30|1.4
2|2024-06-02 08:00:00|8|260|10|1.3

-------Production hours CSV Sample-----
Date,Id,ProductionHrs,ProducedGoods,DefectGoods,IdealCycle
2024-06-15T00:00:00.000,11,21,817,42,1.4
2024-06-15T00:00:00.000,12,19,563,50,1.6
2024-06-16T00:00:00.000,11,22,977,39,1.3
2024-06-16T00:00:00.000,12,11,470,27,1.2
2024-06-16T00:00:00.000,13,17,523,38,1.5
"""

  sample_downtime_data = """
-----DownTime JSON Sample-----------
[
    {
        "Date": "2023-06-21",
        "Id": 1,
        "DownTimeHrs": 1
    },
    {
        "Date": "2023-06-22",
        "Id": 2,
        "DownTimeHrs": 0.5
    },
    {
        "Date": "2023-06-23",
        "Id": 3,
        "DownTimeHrs": 2
    },
    {
        "Date": "2023-06-24",
        "Id": 4,
        "DownTimeHrs": 1.5
    },
    {
        "Date": "2023-06-25",
        "Id": 5,
        "DownTimeHrs": 1
    }
]

-------DownTime hours CSV Sample-----
Date,Id,DownTimeHrs
2024-06-15T00:00:00.000,11,1
2024-06-15T00:00:00.000,12,3
2024-06-16T00:00:00.000,11,0
2024-06-16T00:00:00.000,12,1
2024-06-16T00:00:00.000,13,3


-------DownTime hours Excel Sample-----
ID|Date    |Downtime Hours|Production Goods|Defect Goods|Ideal Cycle
1|2024-06-01 08:00:00|1
1|2024-06-02 08:00:00|3
2|2024-06-01 08:00:00|2
2|2024-06-02 08:00:00|2
"""   
  content = (sample_production_data + sample_downtime_data).encode()
  b64 = base64.b64encode(content).decode()  # some strings <-> bytes conversions necessary here
  href = f'<a href="data:file/txt;base64,{b64}" download="sample_data_formats.txt">⬇️Download sample template.txt</a>'   
  return href


# Column mapping dictionary
column_mapping_production = {
    'Date': ['Date', 'date', 'production_date'],
    'Id': ['Id', 'id', 'machine_id', 'equipment_id'],
    'ProductionHrs': ['ProductionHrs', 'production_hours', 'prod_hours','Production Hours','ProductionHours'],
    'ProducedGoods': ['ProducedGoods', 'produced_goods', 'produced_pieces'],
    'DefectGoods': ['DefectGoods', 'defect_goods', 'defective_goods'],
    'IdealCycle': ['IdealCycle', 'ideal_cycle_time', 'ideal_cycle'],
    'DownTimeHrs': ['DownTimeHrs', 'downtime_hours', 'down_hours']

}

column_mapping_downtime = {
     'Date': ['Date', 'date', 'production_date'],
    'Id': ['Id', 'id', 'machine_id', 'equipment_id'],
     'ProductionHrs': ['ProductionHrs', 'production_hours', 'prod_hours','Production Hours','ProductionHours'],
    'ProducedGoods': ['ProducedGoods', 'produced_goods', 'produced_pieces'],
    'DefectGoods': ['DefectGoods', 'defect_goods', 'defective_goods'],
    'IdealCycle': ['IdealCycle', 'ideal_cycle_time', 'ideal_cycle'],
    'DownTimeHrs': ['DownTimeHrs', 'downtime_hours', 'down_hours']
}

def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.json'):
        return pd.read_json(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")

def standardize_columns(data, column_mapping):
    reverse_mapping = {}
    for standard_name, aliases in column_mapping.items():
        for alias in aliases:
            reverse_mapping[alias] = standard_name
    return data.rename(columns=reverse_mapping)

# File uploads
with st.sidebar.expander("**Upload Data files**"):
    #st.sidebar.title("Upload files")
    production_file = st.file_uploader("**Production Data** ", type=["csv", "json", "xlsx"])
    downtime_file = st.file_uploader("**Downtime Data**", type=["csv", "json", "xlsx"])
st.sidebar.markdown(download_sample_data(), unsafe_allow_html=True)


if production_file is not None and downtime_file is not None:
    try:
        # Read and standardize the uploaded production data file
        production_data = load_data(production_file)
        production_data = standardize_columns(production_data, column_mapping_production)
        
        # Read and standardize the uploaded downtime data file
        downtime_data = load_data(downtime_file)
        downtime_data = standardize_columns(downtime_data, column_mapping_downtime)

        # Ensure the 'Date' columns are in datetime format
        production_data['Date'] = pd.to_datetime(production_data['Date'])
        downtime_data['Date'] = pd.to_datetime(downtime_data['Date'])

        # Check if the required columns are present in either data
        required_columns = ["Date", "Id", "ProductionHrs", "ProducedGoods", "DefectGoods", "DownTimeHrs"]
        production_columns = production_data.columns.tolist()
        downtime_columns = downtime_data.columns.tolist()
        
        if any(column in production_columns for column in required_columns) or \
           any(column in downtime_columns for column in required_columns):
           
            # Merge the production and downtime data on available columns
            common_columns = list(set(production_data.columns) & set(downtime_data.columns))
            data = pd.merge(production_data, downtime_data, on=common_columns, how='outer')
            
            # Calculate availability for each record
            data['Availability'] = (data['ProductionHrs'] - data['DownTimeHrs']) / data['ProductionHrs']

            # Get unique equipment IDs
            equipment_ids = data['Id'].unique()

            # Display all equipment IDs by default
            selected_equipment_id = st.sidebar.selectbox('Select Equipment ID', ['All'] + list(equipment_ids))

            # Filter data based on the selected equipment ID
            if selected_equipment_id == 'All':
                filtered_data = data.copy()  # Show all data if 'All' is selected
            else:
                filtered_data = data[data['Id'] == selected_equipment_id]

            # Calculate OEE for each record
            for index, row in filtered_data.iterrows():
                production_hours = row.get("ProductionHrs", 0)
                downtime_hours = row.get("DownTimeHrs", 0)
                ideal_cycle_time = row.get("IdealCycle", 0)
                total_pieces_produced = row.get("ProducedGoods", 0)
                defect_goods_produced = row.get("DefectGoods", 0)
                good_pieces_produced = total_pieces_produced - defect_goods_produced

                # Calculate availability
                if production_hours > 0:
                    operating_time = production_hours - downtime_hours
                    availability = operating_time / production_hours
                else:
                    availability = 0

                # Calculate performance
                if operating_time > 0 and total_pieces_produced > 0:
                    net_operating_time = ideal_cycle_time * total_pieces_produced
                    performance = net_operating_time / (operating_time * 60)  # converting hours to minutes
                else:
                    performance = 0

                # Calculate quality
                if total_pieces_produced > 0:
                    quality = good_pieces_produced / total_pieces_produced
                else:
                    quality = 0

                # Calculate OEE
                oee = availability * performance * quality

                # Add OEE to the current row
                filtered_data.loc[index, 'OEE'] = oee
                filtered_data.loc[index, 'Availability'] = availability
                filtered_data.loc[index, 'Performance'] = performance
                filtered_data.loc[index, 'Quality'] = quality

            # Display results for each record in a table
            filtered_data_display = filtered_data[['Date', 'Id', 'Availability', 'Performance', 'Quality', 'OEE']]
            filtered_data_display['Availability'] = filtered_data_display['Availability'].apply(lambda x: f"{x:.2%}")
            filtered_data_display['Performance'] = filtered_data_display['Performance'].apply(lambda x: f"{x:.2%}")
            filtered_data_display['Quality'] = filtered_data_display['Quality'].apply(lambda x: f"{x:.2%}")
            filtered_data_display['OEE'] = filtered_data_display['OEE'].apply(lambda x: f"{x:.2%}")
# Calculate average OEE for each equipment
            #avg_oee_data = filtered_data.groupby('Id')['OEE'].mean().reset_index()

# Format OEE values as percentages for display
            #avg_oee_data['OEE'] = avg_oee_data['OEE'].apply(lambda x: f"{x:.2%}")

            avg_oee_data = filtered_data.groupby('Id')['OEE'].mean().reset_index()
            avg_oee_data.columns = ['Id', 'OEE']

# Remove rows with NaN or empty OEE values
            avg_oee_data = avg_oee_data.dropna(subset=['OEE'])

# Format OEE values as percentages for display
            avg_oee_data['OEE'] = avg_oee_data['OEE'].apply(lambda x: f"{x:.2%}")
                     
            # Calculate average OEE for all vehicles on each date
            avg_oee_date_data = filtered_data.groupby('Date')['OEE'].mean().reset_index()

            # Visualize average OEE using a line chart
            fig_avg_oee_date = px.line(avg_oee_date_data, x='Date', y='OEE', title='Average OEE of Vehicles on Each Date',
                                       labels={'Date': 'Date', 'OEE': 'Average OEE'},
                                       hover_data={'OEE': True},
                                       height=350)
            fig_avg_oee_date.update_traces(texttemplate='%{y:.2%}')

            # Calculate average Availability, Performance, and Quality for each equipment
            avg_metrics_data = filtered_data.groupby('Id')[['Availability', 'Performance', 'Quality', 'OEE']].mean().reset_index()
            avg_metrics_data = avg_metrics_data.melt(id_vars=['Id'], value_vars=['Availability', 'Performance', 'Quality', 'OEE'],
                                                     var_name='Metric', value_name='Average')

            # Visualize average Availability, Performance, and Quality using a bar chart
            fig_avg_metrics = px.bar(avg_metrics_data, x='Id', y='Average', color='Metric', barmode='group',
                                     title='Average Availability, Performance, Quality, and OEE of Each Equipment',
                                     labels={'Id': 'Equipment ID', 'Average': 'Average Value'},
                                     hover_data={'Average': True},
                                     height=350)

            # Calculate overall averages for gauges
            overall_avg_availability = filtered_data['Availability'].mean()
            overall_avg_performance = filtered_data['Performance'].mean()
            overall_avg_quality = filtered_data['Quality'].mean()
            overall_avg_oee = filtered_data['OEE'].mean()

            # Create gauge charts for overall averages
            fig_gauge_availability = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall_avg_availability * 100,
                title={'text': "Average Availability"},
                gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#2779B7"}},
                number={'suffix': '%', 'valueformat': '.2f'} ))

            fig_gauge_availability.update_layout(
            width=500, 
            height=330 ) 

            fig_gauge_performance = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall_avg_performance * 100,
                title={'text': "Average Performance"},
                gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#98A1EC"}},
                number={'suffix': '%', 'valueformat': '.2f'} ))

            fig_gauge_performance.update_layout(
            width=500, 
            height=330 ) 


            fig_gauge_quality = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall_avg_quality * 100,
                title={'text': "Average Quality"},
                gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#7FCFF1"}},
                number={'suffix': '%', 'valueformat': '.2f'} ))
            fig_gauge_quality.update_layout(
            width=500, 
            height=330 ) 

            fig_gauge_oee = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall_avg_oee * 100,
                title={'text': "Average OEE"},
                gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#B75FF7"}},
                number={'suffix': '%', 'valueformat': '.2f'} ))
            fig_gauge_oee.update_layout(
            width=500, 
            height=330 )


            # Create a dashboard layout
            st.subheader("Average Metrics Gauges")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.plotly_chart(fig_gauge_availability, use_container_width=True)
            with col2:
                st.plotly_chart(fig_gauge_performance, use_container_width=True)
            with col3:
                st.plotly_chart(fig_gauge_quality, use_container_width=True)
            with col4:
                st.plotly_chart(fig_gauge_oee, use_container_width=True)
            
            col5, col6 = st.columns(2)
            with col5:
                st.plotly_chart(fig_avg_oee_date, use_container_width=True)
            with col6:
                st.plotly_chart(fig_avg_metrics, use_container_width=True)

            col7, col8 = st.columns(2)
            with col7:
                st.write("**Equipment Metric Details**")
                st.dataframe(filtered_data_display,height=300,use_container_width=True)
                #st.write(filtered_data_display)
            with col8:
                st.write('**Average OEE of Each Equipment**')
                #st.write(avg_oee_data,height=300,use_container_width=True)
                st.dataframe(avg_oee_data,height=300,use_container_width=True)

         

        else:
            st.write(f"Error: The uploaded files must contain the required columns in either of the files.")
    except Exception as e:
        st.write(f"An error occurred: {e}")
else:
    st.markdown("Please upload both production and downtime files to proceed.")
    #st.markdown(download_sample_data(), unsafe_allow_html=True)

    
    



 
