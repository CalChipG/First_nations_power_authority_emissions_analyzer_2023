import streamlit as st                          #
import pandas as pd                             #
import plotly.express as px                     #
import plotly.graph_objects as go               #
import requests                                 #
import json                                     #   Import 
import datetime                                 #   All
import numpy as np                              #   Packages 
import streamlit_authenticator as stauth        #   Used
import yaml                                     #
import datetime                                 #
import sqlite3                                  #
import mysql.connector                          #
from streamlit_modal import Modal               #

st.set_page_config(layout="wide")
### Token needed for Mapbox API usage
# token = st.secrets["MAPBOX_TOKEN"]
token = "pk.eyJ1Ijoiam9obmRvZWVkc2Z1ZXIiLCJhIjoiY2xkbXVtd28yMDRrdDN1czR4MHJlMXZoMiJ9.zVn-NQ0bJKI052eCjX9mZw"
###

###Defines a function that when called, reads in Data from Excel sheet and modifies it
num_cols = []
@st.cache(ttl=24*60*60)
def get_data():
    df = pd.read_excel('20220105-2015.xlsx') #Raw excel Data
    cols = ['Reporting Company Trade Name / Nom commercial de la société déclarante', 'Facility Name',
            "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"
            ] #Columns to be read
    for col in cols: #For each column in the file, make the titles all lowercase
        try:
            df[col] = df[col].str.lower()
        except:
            pass
    co2_column = 'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)' #Defines Total emissions column as variable
    df[co2_column] = pd.to_numeric(df[co2_column], errors='coerce') # Loads all numeric values in the Co2 Column above into Dataframe, 
                                                                    #if no value exists, then change that to NaN 
    num_cols.extend(df._get_numeric_data().columns) #Adds those columns to the empty variable defined at the top

    return df       #Returns the Dataframe
#
#
### Putting the Data to use
#
#
df = get_data()  #Calls the function we defined above, this is actually reading the data from the excel sheet.

### Below defines spacing of the web app, as in how wide each column of the site is.
row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('Analyzer')
#
# Defining names for the Chart axes
#
reporting_axis = 'Reporting Company Trade Name / Nom commercial de la société déclarante' 
industry_axis = "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"
co2_column = 'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'

################
### ANALYSIS ###
################

### This creates a function that gets the data which will be used in chart 1
def chart1_data(band, year):                                            # This function has 2 inputs, the Band Name and the Year
    df_filtered = df[df['Reference Year / Année de référence'] == year] # Only gets values that for the year input by user
    df_filtered = df_filtered[df_filtered['Band Name'].isin(band)]      # Only gets bands what match the Band Name selected by user
    df_filtered = df_filtered[df_filtered['Duration'] <= max_dist*3600] # Only gets values within the Driving Duration specified by user
    return df_filtered                                      # Returns the data that matches the parameters above

### Defines what will be on Chart 1
def chart1(df_filtered):  #Creates a new function whose input is the data extracted from chart1_data
    if agree:
        df_tmp = df_filtered.groupby(reporting_axis, as_index=False)[co2_column].sum() # Groups the data by the Company Trade Name
        df_tmp = df_tmp.sort_values(co2_column, ascending=False)                       # Sorts the grouped data above by CO2 emissions from big to small
        top_15 = df_tmp[reporting_axis].head(15).unique()                              # Defines the Top 15 companies that will be plotted
        df_filtered = df_filtered.loc[df_filtered[reporting_axis].isin(top_15)]        # Creates a new table that only holds values for the top 15 emitters
#
###Below we groupd the data by facility name and company, so all facilities belonging to each company, giving a total for each facility 
# belonging to each company, and then sorts from the largest emitting facility to the smallest. Then we reset the index of the data 
# to match the sorting we specified.
    total_df_filtered  = df_filtered.groupby(['Facility Name', 'Reporting Company Trade Name / Nom commercial de la société déclarante'])[
        'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'].sum().sort_values(ascending=False).reset_index()
    
#
### Below we define how the Legend of the chart will be laid out, based on how many companies are in the data frame.
#
    if len(total_df_filtered["Reporting Company Trade Name / Nom commercial de la société déclarante"]) > 10:  
        leg = -1.05
    elif len(total_df_filtered["Reporting Company Trade Name / Nom commercial de la société déclarante"]) > 5:
        leg = -0.5
    else:
        leg = -0.2
#
### Below we define the first chart as a bar graph, where the X-Axis is Company, and Y-Axis is total emissions. The color is based on the 
### Facility Name within each company.
### The rest here just lays out what the chart should look like
    fig = px.bar(total_df_filtered, x="Reporting Company Trade Name / Nom commercial de la société déclarante", y="Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)",
                color='Facility Name')
    fig.update_layout(template='simple_white', xaxis_title='Reporting Company', xaxis={'categoryorder': 'total ascending'},
                    legend=dict(orientation="h", yanchor="top",
                                y=leg, xanchor="right", x=1),
                    yaxis_title='Total Emissions (tonnes CO2e)', title='Total Emissions by Corporation', height=600)  # barmode='stack'
    st.plotly_chart(fig, use_container_width=True)

#
#
###
### Defining data and appearance of the second chart
###
#
#
def chart2_data(band, year):                                                    # Defines new function for the data to be used in Chart 2 by user input Band and Year
    df_filtered = df[df['Reference Year / Année de référence'] == year]         # Only gets values that for the year input by user
    df_filtered = df_filtered[df_filtered['Band Name'].isin(band)]              # Only gets bands what match the Band Name selected by user
    return df_filtered


def chart2(df_filtered):                                                        # Defines a new function for chart 2 based on data above
    
    if agree:
        df_tmp = df_filtered2.groupby(industry_axis, as_index=False)[co2_column].sum()  #Groups data by industry type
        try:
            df_tmp = df_tmp.sort_values(co2_column, ascending=False)                    # Sorts by CO2 Emissions by industry type in descending order
        except:
            pass
        top_15 = df_tmp[industry_axis].head(15).unique()                                # Selects only the top 15 industries
        df_filtered = df_filtered.loc[df_filtered[industry_axis].isin(top_15)]
    
    total_df_filtered = df_filtered.groupby(['Facility Name', industry_axis])[
        'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'].sum().sort_values(ascending=False).reset_index()  
    # As above, this gives us the final data to be used in the chart, where we should total emissions by industry type,
    # where each bar is separated by the facility name. So bar for fossil fuel power generation contains the facilities 
    # that are in that industry type
    
    
    fig = px.bar(total_df_filtered, x="English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais", y="Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)",
                color='Facility Name')

    if len(total_df_filtered["English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"]) > 10:
        leg = -1.05
    else:
        leg = -0.2

    fig.update_layout(template='simple_white', xaxis_title='Industry Type', xaxis={'categoryorder': 'total ascending'},
                    legend=dict(orientation="h", yanchor="top",
                                y=leg, xanchor="right", x=1),
                    yaxis_title='Total Emissions (tonnes CO2e)', title='Total Emissions by Industry Type', height=600)  # barmode='stack'
    st.plotly_chart(fig, use_container_width=True)

#
#
### Chart 3 which gives changes in emissions around a band by year
###
#
#
def chart3_data(band):                              # New function defining data in this chart
    df2 = df[df['Band Name'].isin(band)]            # Pulls out only the rows that contain specified band names 
    color = "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais" # Color is set by Industry type
    top_cats = df2[color].value_counts().head(10).index.tolist() # Calculates the top 10 industries based on frequency
    df2.loc[~df2[color].isin(top_cats), color] = 'Others'        # If an industry is not in the top 10, it belongs to a new group called Others
    return df2


def chart3(df2):                            # Defines function for displaying chart 3
    # Gives total emissions as Y-axis, and year as X-axis, with color coming from industry type.
    fig = px.bar(df2, y='Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)', x='Reference Year / Année de référence',
                color="English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais")

    fig.update_layout(template='simple_white', yaxis_title='Total Emissions (tonnes CO2e)',
                    title='Changes in Emissions Over Time', height=600,
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=1, title='NAICS Code'))

    st.plotly_chart(fig, use_container_width=True)
#
#
### Defining Chart 4
### Displaying scatter plots on a map
#
#
def chart4(data): # Defines function chart4 that takes in a dataframe called "data" as input
    fig = go.Figure()  # Makes an empty figure plot.

    report_col = 'Reporting Company Trade Name / Nom commercial de la société déclarante' # Stores reporting column name

    data[report_col] = data[report_col].fillna('None')  # if there is no value in the data, it puts in None

    data_star = data[data['Location Data Type'].str.lower() == 'band']         # Separates band location from the rest
    data_not_star = data[data['Location Data Type'].str.lower() == 'facility'] # Separates facility location

#
### Below we define how the band location is plotted. 
#
    for fac in data_star[report_col].unique():                  # For each unique entry in the data where Location Data type is band, plotted with star symbol
        data_fac = data_star[data_star[report_col] == fac]      # 
        fig.add_trace(go.Scattermapbox(                         # Adds a point on the map based on long, lat, and name.
            lon=data_fac['Longitude'],
            lat=data_fac['Latitude'],
            text=data_fac['Facility Name'], name=fac,
            mode='markers', marker=dict(
                symbol='star', size=20                          # Plotted as a start of size 20

            )))
#
### Below we define how the facility location is plotted. 
# As above we find all the unique facilities, get their lopcation and plot them.
    for fac in data_not_star[report_col].unique():
        data_fac = data_not_star[data_not_star[report_col] == fac]
        fig.add_trace(go.Scattermapbox(
            lon=data_fac['Longitude'],
            lat=data_fac['Latitude'],
            text=data_fac['Facility Name'], name=fac, 
            mode='markers'))
### Chosing the type of map, outdoors style, North America
    fig.update_layout(
        mapbox_style="outdoors",
        geo_scope='north america', height=700,
    )
### Updates the map plot, setting the center to be the first entry in the facility if available, or fist entry in band. 
    try:
        lon_foc, lat_foc = data_not_star.iloc[0]['Longitude'], data_not_star.iloc[0]['Latitude']
    except:
        lon_foc, lat_foc = data_star.iloc[0]['Longitude'], data_star.iloc[0]['Latitude']

    fig.update_layout(
        mapbox=dict(
            accesstoken=token,
            zoom=2,  # this is kind of like zoom
            # this will center on the point
            center=dict(lat=lat_foc, lon=lon_foc),
        ))
    st.plotly_chart(fig, use_container_width=True)
#
#
### Now we set up how this will all display on a webiste:
#
#

# Here we define how all plot containers should look, and applies a box shadow.
styl = """
<style>
.plot-container{
box-shadow: 4px 4px 8px 4px rgba(0,0,0,0.2);
transition: 0.3s;

}
</styl>
"""
st.markdown(styl, unsafe_allow_html=True)
#
# 
# Here we define what will be on the side bar
#
#
with st.sidebar:
    st.subheader('Configure the Plots')
    band_chart = st.multiselect("Please select Primary Band Name", list(                #Allows users to select multiple bands
            df['Band Name'].unique()), key='band_chart', default=["Tsuut'ina Nation"])
    
    
    data_dist = df[df['Band Name'].isin(band_chart)]                                    # Uses Band location, and a calculation of distance and time to 
    min_d = float(data_dist['Duration'].min()) / 3600                                   # set a radius. Minimum and maximum are defined by 
    max_d = float(data_dist['Duration'].max()) / 3600                                   # The min and max values of driving time for the selected Band

    max_dist = st.slider(
        'Select a range for Driving Duration (in hours)', min_value=min_d, max_value=max_d, value=max_d, step=0.5) # Sets slider min max values and a step
    agree = st.checkbox('Limit to top 15 bars', value=True) # Toggle that limits the amount of bars shown to 15 or All
  
#
# Defines the lay out for a multi-column interface. 
#
row4_spacer1, row4_1, row4_spacer2 = st.columns((.2, 7.1, .2))
# Below gives the title of the chart
with row4_1:
    st.subheader('Total Emissions by Corporation')
row5_spacer1, row5_1, row5_spacer2, row5_2, row5_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
#Below creates a select box for years, and defines the text there.
with row5_1:
    year_chart1 = st.selectbox("Please Select year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart1', index=4)
    st.markdown('This chart shows what corporations are emitting and in what volumes within a '+ str(round(max_dist,2)) +' hour of the selected band in the selected year.')
    st.markdown(
        'The size of bar indicates the total emissions released over the selected year by each corporation.')
    st.markdown(
        'The color of the bar is associated with the name of the emitting facility.')
    st.markdown('Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome.')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
# Plots Chart 1 - Calls the chart1_data function that does the filtering, and then calls chart1 to make the chart from filtered data.
with row5_2:
    df_filtered = chart1_data(band_chart, year_chart1)
    chart1(df_filtered)
    see_data = st.expander('You can click here to see the data 👉') # Defines an expander which contains the data frame used to make the chart
    with see_data:
        st.dataframe(data=df_filtered.astype(str).reset_index(drop=True))


row6_spacer1, row6_1, row6_spacer2 = st.columns((.2, 7.1, .2))
with row6_1:
    st.subheader('Total Emissions by Industry Type')
row7_spacer1, row7_1, row7_spacer2, row7_2, row7_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
with row7_1:
    year_chart2 = st.selectbox("Please select year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart2', index=4)
    st.markdown('''This chart describes what types of industries are operating within a '''+ str(round(max_dist,2)) +''' hour of the selected band name. 

The size of bar indicates the total emissions released over the selected year. 

The color of the bar is associated with the name of the emitting facility. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome. 
''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')

# Defines how the second chart will be displayed, plus the expander that holds the data frame. 
with row7_2:
    df_filtered2 = chart2_data(band_chart, year_chart2)
    chart2(df_filtered2)
    see_data2 = st.expander('You can click here to see the data 👉')
    with see_data2:
        st.dataframe(data=df_filtered2.astype(str).reset_index(drop=True))

# Defines the 3rd chart, similar to above.
row8_spacer1, row8_1, row8_spacer2 = st.columns((.2, 7.1, .2))
with row8_1:
    st.subheader('Changes in Emissions Over Time')
row9_spacer1, row9_1, row9_spacer2, row9_2, row9_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
with row9_1:
    st.markdown('''This chart describes changes in emissions over time within a '''+ str(round(max_dist,2)) +''' hour of the selected First Nation. 

The size of bar indicates the total emissions released over the selected year. 

The color of the bar is associated with the type of industry. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome. ''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
with row9_2:
    df2 = chart3_data(band_chart)
    chart3(df2)
    see_data3 = st.expander('You can click here to see the data 👉')
    with see_data3:
        st.dataframe(data=df2.astype(str).reset_index(drop=True))

#Defines the 4th chart.
row10_spacer1, row10_1, row10_spacer2 = st.columns((.2, 7.1, .2))
with row10_1:
    st.subheader('Map of Emitting Facilities and Bands')
row11_spacer1, row11_1, row11_spacer2, row11_2, row11_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
with row11_1:
    year_chart4 = st.selectbox("Please elect year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart4', index=4)
    df_filtered4 = chart1_data(band_chart, year_chart4)


    st.markdown('''This map describes emitting facilities within a '''+ str(round(max_dist,2)) +''' hour of the selected bands. All bands are displayed as stars. 

The circles on the map describe facility locations. The circles are colored by the polluting/emitting corporation. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome.''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
with row11_2:
    
    chart4(df_filtered4)
    see_data4 = st.expander('You can click here to see the data 👉')
    with see_data4:
        st.dataframe(data=df_filtered4.astype(str).reset_index(drop=True))



