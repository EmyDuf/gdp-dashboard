
# -----------------------------------------------------------------------------
# Declare some useful functions.
import altair as alt
import streamlit as st
import pandas as pd
import math
import datetime
from pathlib import Path

import os
os.system("pip install -r requirements.txt")
import plotly.express as px
from streamlit_player import st_player
import geopandas as gpd
#from ipyleaflet import Map, Marker
from streamlit_folium import folium_static
import pydeck as pdk
import folium
import streamlit_pannellum
from streamlit_pannellum import streamlit_pannellum

import json
import geopandas as gpd
import pyproj

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(layout="wide",    page_title='Hackaviz 2025 : La Garonne',
    page_icon=':ocean:',) # This is an emoji shortcode. Could be a URL too.)
#@m = folium.Map(location=[43.59966,1.44043,], zoom_start=11, tiles='OpenStreetMap')
#folium_static(m)

# Primary accent for interactive elements
primaryColor = '#d33682'
# Background color for the main content area
backgroundColor = '#002b36'
# Background color for sidebar and most interactive widgets
secondaryBackgroundColor = '#586e75'
# Color used for almost all text
textColor = '#fafafa'
# Font family for all text in the app, except code blocks
# Accepted values (serif | sans serif | monospace) 
# Default: "sans serif"
font = "sans serif"



# -----------------------------------------------------------------------------
#@st.cache_data
def get_data_station():
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/station.geoparquet'
    gdp_df_station = gpd.read_parquet(DATA_FILENAME)


    gdp_df_station['st_x'] = gdp_df_station['geometry'].x
    gdp_df_station['st_y'] = gdp_df_station['geometry'].y
    return gdp_df_station

gdp_df_station = get_data_station()

def get_data_debit():
    """Grab data from a parquet file.
    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: #@st.cache_data(ttl='1d')    
    """    
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/debit_5_crues.parquet'
    raw_debit_df = pd.read_parquet(DATA_FILENAME)

    # Pivot 
    gdp_df_debit = raw_debit_df.melt(
        ['code_station','code_crue','date_observation'],
        'debit_moyen_journalier',
    )
    # Convert years from string to integers
    gdp_df_debit['code_crue'] = pd.to_numeric(gdp_df_debit['code_crue'])
    gdp_df_debit['x'] = pd.to_datetime(gdp_df_debit['date_observation'], format="%Y/%m/%d")
    gdp_df_debit["date_m_d"] = pd.to_datetime(gdp_df_debit["x"].dt.strftime("2022-%m-%d-"), errors="coerce")
            #gdp_df_debit['date_m_d'] = gdp_df_debit['date_observation'].dt.month
            #gdp_df_debit["date_m_d"] = pd.to_datetime(gdp_df_debit["date_observation"].dt.strftime("%d-%m-2022"), errors="coerce")
            # create columns for x and color/trace
            #gdp_df_debit["x"] = pd.to_datetime(gdp_df_debit["date_observation"].dt.strftime("%d-%b-2022"), errors="coerce")
            #gdp_df_debit["year"] = gdp_df_debit["date_observation"].dt.year
            #gdp_df_debit['m_d'] = gdp_df_debit['date_observation'].dt.strftime("%d/%b")

    # Merge with station 
    #gdp_df_station
    return gdp_df_debit

gdp_df_debit = get_data_debit()

def get_data_haut():
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.

    DATA_FILENAME = Path(__file__).parent/'data/hauteur_eau_9_crues.parquet'
    raw_debit_df = pd.read_parquet(DATA_FILENAME)

    # Pivot 
    gdp_df_haut = raw_debit_df.melt(
        ['code_station','code_crue','date_heure'],
        'hauteur'
    )
    # Convert years from string to integers
    gdp_df_haut['code_crue'] = pd.to_numeric(gdp_df_haut['code_crue'])
    gdp_df_haut['x'] = pd.to_datetime(gdp_df_haut['date_heure'], format="%Y/%m/%d %H:%M:%S" )
    gdp_df_haut["date_m_d"] = pd.to_datetime(gdp_df_haut["x"].dt.strftime("2022-%m-%d"), errors="coerce")
    gdp_df_haut = gdp_df_haut.loc[gdp_df_haut['date_heure'].dt.hour == 12]

    return gdp_df_haut

gdp_df_haut = get_data_haut()




# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
st.header("Une petite histoire de Garonne")
st.caption("Explication du sujet. :ocean: :mountain: :cloud:  :snowflake: ")

# Add some spacing

min_value_debit = gdp_df_debit['code_crue'].min()
max_value_debit = gdp_df_debit['code_crue'].max()

st.logo("data/n.svg")

#date_crues = st.sidebar.radio("Années de crues", gdp_df_debit['code_crue'].unique())
date_crues = st.sidebar.multiselect("Années de crues", gdp_df_debit['code_crue'].unique(), 2022)

from_year, to_year = st.sidebar.slider(
    'Un retour dans le temps',
    min_value=max_value_debit,
    value=[min_value_debit, max_value_debit],max_value=max_value_debit)

date_crues = st.sidebar.date_input("Isoler les dates avant et après la crue", (datetime.date(2022, 1, 1), datetime.date(2022, 1, 10)))
#st.write("Your birthday is:", date_crues)

#st.sidebar.number_input
input_1 = st.sidebar.number_input('Nombre de jour avant et après la crue', min_value=1.0, max_value=5.0, value=1.0, step=1.0)

# Filter station
station = gdp_df_debit['code_station'].unique()
if not len(station):
    st.warning("Selectionner au moins une station")

selected_station = st.sidebar.multiselect('Quelle station souhaitez-vous regarder ?', station, ['O125251001'])

all = st.sidebar.checkbox("Au dessus de 1 500 000 l/s soit le débit qui peut emporter une maison ou détruire les fondations", value=True) #.query("debit_moyen_journalier>1500000.0")



''
#https://my.sirv.com/#/browse/Images?preview=%2FImages%2Fpont_neuf.jpg
#Detail https://pannellum.org/documentation/reference/
DATA_FILENAME = Path(__file__).parent/'data/Photo360.jpg'
streamlit_pannellum(
    config={
      "default": {
        "firstScene": "first", #"circle",
        #"sceneFadeDuration": 1000
      },
      "scenes": {
        "first": {
          "title": "La Garonne",
          "author": "vue du pont neuf à Toulouse",
          "type": "equirectangular",
          "panorama": "https://hackaviz.sirv.com/Images/pont_neuf_v2.jpg",
          #"preview": "/data/pont_neuf(1).jpg",
          "haov": 110, #149.87  panorama’s horizontal angle of view, in degrees. Defaults to 360
          "vaov": 60, #54.15  panorama’s vertical angle of view, in degrees. Defaults to 180
          "vOffset":-5, # vertical offset of the center of the equirectangular image from the horizon, in degrees. Defaults to 0
          "showZoomCtrl": True,
          "orientationOnByDefault" : False,
          "autoLoad": True,
          "hfov": 15, #zoom
          "minYaw" : -90,
          "maxYaw" : 90,
          #"author": "Emy",
          "hotSpots": [
            {
              "pitch": 4,
              "yaw": 15,
              "type": "info",
              "text": "Un effet d'optique rend visible les Pyrénées qui sont pourtant à 120km de distance. Le phénomène, classique en hiver, est lié au vent du sud. Il est aussi signe de sécheresse."
            },
            {
              "pitch": -10,
              "yaw": -10.7,
              "type": "info",
              "text": "Le Pont Neuf date de 1544, ce qui fait de lui le plus Vieux pont de la Garonne. Les travaux ont durés un siècle où le chantier a été soumis à des crues dévastatrices et à un lit de la Garonne trompeur.",
              "sceneId": "second"
            },
            {
              "pitch": 0,
              "yaw": -10,
              "type": "scene",
              "text": "Second scene",
              "sceneId": "second"
            }
          ],
        },
        "second": {
          "title": "My second example",
          "type": "equirectangular",
          "panorama": "https://pannellum.org/images/alma.jpg",
          "preview": "/data/pont_neuf.jpg",
          "autoLoad": True,
          #"author": "always Me",
          "hotSpots": [
            {
              "pitch": 15,
              "yaw": 0,
              "type": "info",
              "text": "This is an info."
            },
            {
              "pitch": 0,
              "yaw": -10,
              "type": "scene",
              "text": "First scene",
              "sceneId": "first"
            },
            #{
            #"createTooltipFunc": hotspot, #function name
            #"createTooltipArgs": "Baltimore Museum of Art"
            #},
          ],
        }
      }
    }
)

#st.title('Split steps of the story')
tab1, tab2, tab3 = st.tabs([ "Débit", "Hauteur d'eau", "S''ambiancer"])

with tab1:
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    # Filter the data
    filtered_gdp_df_debit = gdp_df_debit[
    (gdp_df_debit['code_station'].isin(selected_station))
    & (gdp_df_debit['code_crue'] <= to_year)
    & (from_year <= gdp_df_debit['code_crue'])]

    st.write('Débit')
    st.header('Débit', divider='gray')


    fig = px.line(filtered_gdp_df_debit, x="date_m_d", y="value", title=" ",
    color='code_crue', color_discrete_sequence=px.colors.sequential.Magenta, #Magma_r Magenta Agsunset_r
    facet_row='code_station' ) #.update_layout( xaxis={"dtick": "M1", "tickformat": "%d-%b"})
    st.plotly_chart(fig)
    fig.write_image("data/fig1.svg", engine="kaleido")
    ''

    #st.line_chart(filtered_gdp_df_debit, x='date_observation', y='value', color='code_station',)
    first_year = gdp_df_debit[gdp_df_debit['code_crue'] == from_year]
    last_year = gdp_df_debit[gdp_df_debit['code_crue'] == to_year]

    ''
    # -----------------------------------------------------------------------------

    # Filter the dataframe based on the widget input and reshape it.
    df_filtered = gdp_df_debit[(gdp_df_debit["code_station"].isin(selected_station)) & (gdp_df_debit["code_crue"].between(from_year, to_year))]
    df_reshaped = df_filtered.pivot_table(
        index="code_crue", columns="code_station", values="value", aggfunc="sum", fill_value=0
    )
    df_reshaped = df_reshaped.sort_values(by="code_crue", ascending=False)


    # Display the data as a table using `st.dataframe`.
    st.dataframe(
        df_filtered,
        use_container_width=True,
        column_config={"code_crue": st.column_config.TextColumn("code_crue")},
    )

with tab2:
    st.write("Hauteur d'eau")

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    # Filter the data
    filtered_gdp_df_haut = gdp_df_haut[
    (gdp_df_haut['code_station'].isin(selected_station))
    & (gdp_df_haut['code_crue'] <= to_year)
    & (from_year <= gdp_df_haut['code_crue'])]
    
    st.write("Hauteur d'eau")
    st.header("Hauteur d'eau", divider='gray')


    fig = px.line(filtered_gdp_df_haut, x="date_m_d", y="value", title=" ",
    color='code_crue', facet_row='code_station' ) #.update_layout( xaxis={"dtick": "M1", "tickformat": "%d-%b"})
    st.plotly_chart(fig)
    ''

    #st.line_chart(filtered_gdp_df_debit, x='date_observation', y='value', color='code_station',)
    first_year = gdp_df_haut[gdp_df_haut['code_crue'] == from_year]
    last_year = gdp_df_haut[gdp_df_haut['code_crue'] == to_year]

    ''
    # -----------------------------------------------------------------------------

    # Filter the dataframe based on the widget input and reshape it.
    df_filtered_haut = gdp_df_haut[(gdp_df_haut["code_station"].isin(selected_station)) & (gdp_df_haut["code_crue"].between(from_year, to_year))]
    df_reshaped_haut = df_filtered_haut.pivot_table(
        index="code_crue", columns="code_station", values="value", aggfunc="sum", fill_value=0
    )
    df_reshaped_haut = df_reshaped_haut.sort_values(by="code_crue", ascending=False)


    # Display the data as a table using `st.dataframe`.
    st.dataframe(
        df_filtered_haut,
        use_container_width=True,
        column_config={"code_crue": st.column_config.TextColumn("code_crue")},
    )

with tab3:
    st.write("S'ambiancer")
    # 🎵 ⛰️ Add a video with my favorite music that have a relation with the mountain (or juste the sound) 
    #"https://www.youtube.com/watch?v=t51_2ZEyuj4&pp=ygUKI2FubmFsZW9uZQ%3D%3D" "https://soundcloud.com/annaleone/still-i-wait?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
    #"https://soundcloud.com/annaleone/sets/still-i-wait?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing" "https://soundcloud.com/ocie-elliott/wait-for-you?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
    #"https://soundcloud.com/indiefolkcentral/ocie-elliott-down-by-the-water?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing" "https://soundcloud.com/dominika-zolnierczuk/sets/ocie-elliott?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
    video_url = "https://soundcloud.com/ocie-elliott/like-a-river?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
    st_player(video_url) #, subtitles="subtitles.vtt" subtitles="subtitles.vtt"Interessant d'avoir le texte qui défile ! 


    
#
#''
#
#cols = st.columns(4)
#
#for i, country in enumerate(selected_countries):
#    col = cols[i % len(cols)]
#
#   with col:
#        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
#        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
#
#        if math.isnan(first_gdp):
#            growth = 'n/a'
#            delta_color = 'off'
#        else:
#            growth = f'{last_gdp / first_gdp:,.2f}x'
#            delta_color = 'normal'
#
#        st.metric(
#            label=f'{country} GDP',
#            value=f'{last_gdp:,.0f}B',
#            delta=growth,
#            delta_color=delta_color
#        )


#st.title('A Simple Geocoder')
#st.markdown('This app uses the [OpenRouteService API](https://openrouteservice.org/) '
#    'to geocode the input address and siplay the results on a map.')

#address = st.text_input('Enter an address.')

#_____
#_____

#Test non fonctionnel
#center = (52.204793, 360.121558)
#map = Map(center=center, zoom=12)

# Add a draggable marker to the map
# Dragging the marker updates the marker.location value in Python
#marker = Marker(location=center, draggable=True)
#map.add_control(marker)

#st.map(map)




view_state = pdk.ViewState(latitude=43.29966,
                           longitude=1.36743,
                           zoom=9,
                           pitch=60,bearing=190 )

d1 = {'lon': [1.44043, 1.44043], 'lat': [43.59966, 43.59966], 'name':['meA', 'meB'], 'prec':[100,300], 'temp':[10,30], 'elevationValue':[100,300]}
df_map1 = pd.DataFrame(data=d1)

tooltip = {
    "html":
        "<b>Name:</b> {name} <br/>"
        "<b>Rain:</b> {prec} mm<br/>",
    "style": {
        "backgroundColor": "steelblue",
        "color": "black",
    }
}

slayer = pdk.Layer(
    type='ScatterplotLayer',
    data=df_map1,
    get_position=["lon", "lat"],
    get_color=["255-temp*3", "31+temp*2", "31+temp*3"],
    get_line_color=[0, 0, 0],
    #get_radius=1750,
    pickable=True,
    onClick=True,
    filled=True,
    line_width_min_pixels=10,
    opacity=2,
)

layert1 = pdk.Layer(
    type="TextLayer",
    data=df_map1,
    pickable=False,
    get_position=["lon", "lat"],
    get_text="name",
    get_size=3000,
    sizeUnits='meters',
    get_color=[0, 0, 0],
    get_angle=0,
    # Note that string constants in pydeck are explicitly passed as strings
    # This distinguishes them from columns in a data set
    getTextAnchor= '"middle"',
    get_alignment_baseline='"bottom"',
    get_radius=200,
)

mapstyle = st.sidebar.selectbox(
    "Choose Map Style:",
    options=["mapbox://styles/emi2020/cm8arzmix00g201s36ex4bwtl","mapbox://styles/mapbox/outdoors-v11", "light", "dark", "satellite", "road"],
    format_func=str.capitalize,
    placeholder="mapbox://styles/emi2020/cm8arzmix00g201s36ex4bwtl",
)

pp = pdk.Deck(
    initial_view_state=view_state,
    map_provider='mapbox',
    map_style=f"{mapstyle}" ,  # 'light', 'dark', 'satellite', 'road' #pdk.map_styles.mapstyle, #"light", "dark", "satellite", "road"
    layers=[
        slayer,
        layert1,
    ],
    tooltip=tooltip
)

deckchart = st.pydeck_chart(pp)

#data
DATA_FILENAME = Path(__file__).parent/'data/station.geoparquet'
raw_station_df = gpd.read_parquet(DATA_FILENAME)

#in_geoparquet = "station.geoparquet"
#listings_df = gpd.read_geoparquet(in_geoparquet)


st.pydeck_chart(
    pdk.Deck(
        map_style=f"{mapstyle}",
        initial_view_state=pdk.ViewState(
        latitude=43.29966,
        longitude=1.36743,
        zoom=9,pitch=60,bearing=190 
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=gdp_df_station,
                get_position=["st_y", "st_x",],
                get_color=[200,20,20],
                get_radius=120
            )
        ],))
#map.setTerrain({ "source": "mapbox-dem-2", 'exaggeration': 1.5 })


#st.image("https://placekitten.com/200/300")

#st.markdown(
#    """
#    <style>
#    img {
#        cursor: pointer;
#        transition: all .2s ease-in-out;
#    }
#    img:hover {
#        transform: scale(1.1);
#    }
#    </style>
#    """,
#    unsafe_allow_html=True,
#)

