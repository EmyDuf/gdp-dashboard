
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
#from streamlit_folium import folium_static
import pydeck as pdk
#import folium
import streamlit_pannellum
from streamlit_pannellum import streamlit_pannellum
#import dash_pannellum

#import dash
#from dash import html
#import dash_pannellum

from plotly.subplots import make_subplots
from plotly_calplot import calplot
#libxmp #ipyleaflet #pyproj #json #folium
#import json
import geopandas as gpd
#import pyproj
#lxml
#libxmp2 #lxml #python-xmp-toolkit #libxmp
#streamlit_pannellum

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(layout="wide",    page_title='Hackaviz 2025 : La Garonne',
    page_icon=':ocean:',initial_sidebar_state='collapsed',) # This is an emoji shortcode. Could be a URL too.)
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
    DATA_FILENAME = Path(__file__).parent/'data/station.geoparquet'
    df_station = pd.read_parquet(DATA_FILENAME)
    gdp_df_debit = gdp_df_debit.merge(df_station[['code_station','libelle_cours_eau','altitude_site','surface_bassin_versant']], on=['code_station', 'code_station'])

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

    DATA_FILENAME = Path(__file__).parent/'data/station.geoparquet'
    df_station = pd.read_parquet(DATA_FILENAME)
    gdp_df_haut = gdp_df_haut.merge(df_station[['code_station','libelle_cours_eau','altitude_site','surface_bassin_versant']], on=['code_station', 'code_station'])

    return gdp_df_haut

gdp_df_haut = get_data_haut()

def get_data_pluv():
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.

    DATA_FILENAME = Path(__file__).parent/'data/pluviometrie.parquet'
    raw_pluv_df = pd.read_parquet(DATA_FILENAME)

    # Pivot 
    #gdp_df_pluv = raw_pluv_df.melt(
    #    ['code_pluviometre','code_crue','date_observation'],
    #    'precipitation'
    #)
    gdp_df_pluv = raw_pluv_df

    # Convert years from string to integers
    gdp_df_pluv['code_crue'] = pd.to_numeric(gdp_df_pluv['code_crue'])
    gdp_df_pluv['x'] = pd.to_datetime(gdp_df_pluv['date_observation'], format="%Y/%m/%d" )
    gdp_df_pluv["date_m_d"] = pd.to_datetime(gdp_df_pluv["x"].dt.strftime("2022-%m-%d"), errors="coerce")
    #gdp_df_pluv = gdp_df_pluv.loc[gdp_df_pluv['date_heure'].dt.hour == 12]

    return gdp_df_pluv

gdp_df_pluv = get_data_pluv()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
st.header("Les crues de la Garonne")

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

# Calendrier
#date_crues = st.sidebar.date_input("Isoler les dates avant et après la crue", (datetime.date(2022, 1, 1), datetime.date(2022, 1, 10)))

#st.sidebar.number_input
#input_1 = st.sidebar.number_input('Nombre de jour avant et après la crue', min_value=1.0, max_value=5.0, value=1.0, step=1.0)

# Filter station
station = gdp_df_debit['code_station'].unique()
if not len(station):
    st.warning("Selectionner au moins une station")

selected_station = st.sidebar.multiselect('Quelle station souhaitez-vous regarder ?', station,  
['O125251001', 'O029003001', 'O059251001', 'O098401001', 'O166291001', 'O171251001', 'O171253001', 'O200001001'])
#,'O082001001''O200008001' and , 'O200004001' is not part of the options
#['MURET','MANCIOUX','ROQUEFORT-SUR-GARONNE','MURET','FOIX','CALMONT','AUTERIVE','AUTERIVE','PORTET-SUR-GARONNE','TOULOUSE'


# Filtrer gros débit
#all = st.sidebar.checkbox("Au dessus de 1 500 000 l/s soit le débit qui peut emporter une maison ou détruire les fondations", value=True) #.query("debit_moyen_journalier>1500000.0")
#https://my.sirv.com/#/browse/Images?preview=%2FImages%2Fpont_neuf.jpg
#Detail https://pannellum.org/documentation/reference/
#DATA_FILENAME = Path(__file__).parent/'data/Photo360.jpg'



streamlit_pannellum(
    config={
      "default": {
        "firstScene": "first", #"circle",
        "sceneFadeDuration": 1000
      },
      "scenes": {
        "first": {
          "title": "La Garonne",
          "maxLevel": 120,
          "compass":True,
          "extension": "jpg",
          #"author": "vue du pont neuf à Toulouse",
          "type": "equirectangular", #"multires",
          "panorama": "https://hackaviz.sirv.com/Images/pont_neuf_v2.jpg",
          #"preview": "/data/pont_neuf(1).jpg",
          "haov": 110, #149.87  panorama’s horizontal angle of view, in degrees. Defaults to 360
          "vaov": 70, #54.15  panorama’s vertical angle of view, in degrees. Defaults to 180
          "vOffset":-3, # vertical offset of the center of the equirectangular image from the horizon, in degrees. Defaults to 0
          "showZoomCtrl": True,
          "orientationOnByDefault" : False,
          "autoLoad": True,
          "hfov": 3, #zoom
          "minYaw" : -900,
          "maxYaw" : 90,

          #"author": "Emy",
          "hotSpots": [
            {
              "pitch": 8.2,
              "yaw": 15,
              "type": "info",
              #"haov": 110, #149.87  panorama’s horizontal angle of view, in degrees. Defaults to 360
              #"vaov": 70,
              "text": "Effet d'optique qui rend visible les Pyrénées à 120km de distance. Le phénomène, classique en hiver, est lié au vent du sud. Signe de sécheresse également ?",
              "sceneId": "first",
            },
            {
              "pitch": -10,
              "yaw": -10.7,
              "type": "info",
              "text": "Le Pont Neuf date de 1544, ce qui fait de lui le plus Vieux pont de la Garonne. Les travaux ont durés un siècle où le chantier a été soumis à des crues dévastatrices et à un lit de la Garonne trompeur.",
              "sceneId": "first",
              #"targetPitch": -10,
              #"targetYaw": -10.7
            },
            {
              #"pitch": 0,
              "yaw": -10,
              "type": "scene",
              "text": "Se situer",
              "sceneId": "second"
            }
          ]
        },
        "second": {
          #"compass":True,
          #"title": "Le pont",
          "type": "equirectangular", #"equirectangular",
          "panorama": "https://hackaviz.sirv.com/Images/image_2.jpg",
          #"preview": "/data/image_2.jpg",
          "autoLoad": True,
          "yaw":-90,
          #"width" : 1000,
          #"height" : 400,
          "hotSpots": [
            {
              "pitch": 15,
              "yaw": -90,
              "type": "scene",
              "text": "Retourner au panorama.",
              "sceneId": "first"
            }],

        },
    } 
})

#st.title('Split steps of the story')
tab0, tab1, tab2, tab3, tab4 = st.tabs([ "Affluents", "Débit", "Hauteur de crue", "Pluviométrie", "S'ambiancer"])
with tab0:
    st.header('Affluents', divider='gray')
    st.caption("Durant son parcours, La Garonne collecte l'eau qui vient de tous les points du bassin versant : affluents, pluie, glaciers, eau souterraine. Les mesures hydrométriques sont effectuées sur les bassins versants de la Garonne : les principaux cours d'eau qui alimentent le débit de la Garonne sont Le Grand Hers, L'Ariège, Le Salat et La Louge). :ocean: :mountain: :cloud:  :snowflake: ")

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
                            zoom=9,pitch=60,bearing=180)

    d1 = {'lon': [1.44043, 0.97392], 'lat': [43.59966, 43.154442], 'name':['Toulouse', 'Le Salat'], 'temp':[100,16],}
    df_map1 = pd.DataFrame(data=d1)

    #MAPBOX_API_KEY= "pk.eyJ1IjoiZW1pMjAyMCIsImEiOiJjazRiaG8xY20wZHo1M25tbnF6amhyMnZwIn0.Y566I7K3rIBjF24gbDBbZQ"
    #ELEVATION_DECODER = {"rScaler": 256, "gScaler": 1, "bScaler": 1 / 256, "offset": -32768}
    #SURFACE_IMAGE =f"https://api.mapbox.com/v4/mapbox.satellite/{{z}}/{{x}}/{{y}}@2x.png?access_token={MAPBOX_API_KEY}"
    #TERRAIN_IMAGE="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
    #terrain_layer = pdk.Layer( "TerrainLayer",
    #            elevation_decoder=ELEVATION_DECODER,
    #            texture=SURFACE_IMAGE,
    #            elevation_data=TERRAIN_IMAGE)

    tooltip = {
        "html":
            "<b>Name:</b> {name} <br/>"
            "<b>Bassin versant:</b> {temp} %<br/>",
        "style": {
            "backgroundColor": "steelblue",
            "color": "black",
        }
    }

    slayer = pdk.Layer(
        type='ScatterplotLayer',
        data=df_map1,
        get_position=["lon", "lat"],
        get_color=["255-temp*3", "18+temp*2", "18+temp*3"],
        get_line_color=[10, 0, 0],
        #get_radius=1750,
        pickable=True,
        onClick=True,
        filled=True,
        line_width_min_pixels=10,
        opacity=2,
        #auto_highlight=True,
        #elevation_scale=50,
        #elevation_range=[0, 3000],
        #extruded=True,                 
        #coverage=1
    )

    layert1 = pdk.Layer(
        type="TextLayer",
        data=df_map1,
        pickable=False,
        get_position=["lon", "lat"],
        get_text="name",
        get_size=1200,
        sizeUnits='meters',
        get_color="[10, 0, 0]",
        get_angle=0,
        # Note that string constants in pydeck are explicitly passed as strings
        # This distinguishes them from columns in a data set
        getTextAnchor= '"end"', #'"start"', #middle
        get_alignment_baseline='"bottom"', #top center "bottom"
        get_radius=200,
    )

    mapstyle = st.sidebar.selectbox(
        "Choose Map Style:",
        options=["mapbox://styles/mapbox/outdoors-v11", "light", "dark", "satellite", "road"],
        format_func=str.capitalize,
        placeholder="mapbox://styles/mapbox/outdoors-v11", #mapbox://styles/emi2020/cm91i229e008901sdbx6i5scy
    )

    pp = pdk.Deck(initial_view_state=view_state,
        map_provider='mapbox',
        map_style=f"{mapstyle}" ,  # 'light', 'dark', 'satellite', 'road' #pdk.map_styles.mapstyle, #"light", "dark", "satellite", "road"
        layers=[
            slayer,
            layert1,
        ],
        tooltip=tooltip
    )

    deckchart = st.pydeck_chart(pp)



with tab1:

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    # Filter the data
    filtered_gdp_df_debit = gdp_df_debit[
    (gdp_df_debit['code_station'].isin(selected_station))
    & (gdp_df_debit['code_crue'] <= to_year)
    & (from_year <= gdp_df_debit['code_crue'])]

    filtered_gdp_df_debit = filtered_gdp_df_debit.sort_values(by=['code_crue', 'surface_bassin_versant','altitude_site'])

    st.header('Débit', divider='gray')   
    st.caption("Les débits des différents affluents annoncent les crues en aval. :ocean: :mountain: :cloud:  :snowflake: ")

    fig1 = px.line(filtered_gdp_df_debit[filtered_gdp_df_debit["code_station"].apply(lambda x: 'O200001001' not in x)] , y="value", x="date_m_d", color="code_crue",color_discrete_sequence=px.colors.sequential.Magenta, hover_data='date_observation',facet_row='libelle_cours_eau' ,  category_orders={"libelle_cours_eau": ["Le Grand Hers", "L'Ariège", "Le Salat", "La Louge"],  "code_crue": ["2022", "2000", "1977", "1952", "1905"] }, #gray
        ) #width = 1300, height = 600,.update_traces(side="positive", width=1)#, "time": ["Lunch", "Dinner"] box=True, points="altitude_site") #hover_data=filtered_gdp_df_debit.code_crue,
    fig1.update_yaxes(visible=False, showgrid =True, showticklabels=True)
    fig1.update_xaxes(
    dtick="M1",
    tickformat="%b")

    #fig1.add_vrect( # ou vline pour verticale avec x=...
    #          x0="2022-01-10", x1="2022-01-12", line_dash="dot")
    ''
    fig1.add_trace(px.line(filtered_gdp_df_debit.query("code_station == 'O200001001'"), y="value", x="date_m_d", color="code_crue", color_discrete_sequence=px.colors.sequential.Magenta, hover_data='date_observation',facet_col='libelle_cours_eau' ).data[0])
    
    fig1.add_vrect( x0="2022-01-10", x1="2022-01-12",
                   col=1, # numéro de la colonne (les figures de droites)
                   #annotation_text="2022",
                   #annotation_position="top left",
                   fillcolor="pink", opacity=0.2, line_width=0.1) # ou vline pour verticale avec x=...x=1, line_dash="dot",annotation_text="11 janvier 2022",annotation_position="bottom right")
   
    fig1.add_vrect( x0="2022-02-04", x1="2022-02-06",
                   col=1, # numéro de la colonne (les figures de droites)
                   #annotation_text="1952",
                   #annotation_position="top left",
                   fillcolor="pink", opacity=0.2, line_width=0.1) # ou vline pour verticale avec x=...x=1, line_dash="dot",annotation_text="11 janvier 2022",annotation_position="bottom right")

    fig1.add_vrect( x0="2022-05-17", x1="2022-05-19",
                   col=1, # numéro de la colonne (les figures de droites)
                   #annotation_text="1977",
                   #annotation_position="top left",
                   fillcolor="pink", opacity=0.2, line_width=0.1) # ou vline pour verticale avec x=...x=1, line_dash="dot",annotation_text="11 janvier 2022",annotation_position="bottom right")
    
    fig1.add_vrect( x0="2022-06-11", x1="2022-06-13",
                   col=1, # numéro de la colonne (les figures de droites)
                   #annotation_text="2000",
                   #annotation_position="top left",
                   fillcolor="pink", opacity=0.2, line_width=0.1) # ou vline pour verticale avec x=...x=1, line_dash="dot",annotation_text="11 janvier 2022",annotation_position="bottom right")

    #fig1.update_layout(yaxis_title=True)
    fig1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    fig1.for_each_trace(lambda t: t.update(name=t.name.split("=")[0]))       
    fig1.update_layout(xaxis_title=None)
    fig1.update_layout(showlegend=True)
    st.plotly_chart(fig1)


    #fig2 = px.line(filtered_gdp_df_debit.query("code_station == 'O200001001'"), y="value", x="date_m_d", color="code_crue", color_discrete_sequence=px.colors.sequential.Magenta, hover_data='date_observation',facet_col='libelle_cours_eau' )
    #st.plotly_chart(fig2)

    #fig = px.line(filtered_gdp_df_debit, x="date_m_d", y="value", title=" ",
    #color='code_crue', color_discrete_sequence=px.colors.sequential.Magenta, #Magma_r Magenta Agsunset_r
     #facet_row='altitude_site',.update_layout( xaxis={"dtick": "M1", "tickformat": "%d-%b"})
        #fig.write_image("data/fig1.svg", engine="kaleido")

    #st.line_chart(filtered_gdp_df_debit, x='date_observation', y='value', color='code_station',)
    first_year = gdp_df_debit[gdp_df_debit['code_crue'] == from_year]
    last_year = gdp_df_debit[gdp_df_debit['code_crue'] == to_year]

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
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    # Filter the data
    filtered_gdp_df_haut = gdp_df_haut[
    (gdp_df_haut['code_station'].isin(selected_station))
    & (gdp_df_haut['code_crue'] <= to_year)
    & (from_year <= gdp_df_haut['code_crue'])]
    
    st.header("Hauteur de crue", divider='gray')
    st.caption("Une hauteur de crue dépassant les 4 mètres. :ocean: :mountain: :cloud:  :snowflake: ")

    #st.line_chart(filtered_gdp_df_debit, x='date_observation', y='value', color='code_station',)
    first_year = gdp_df_haut[gdp_df_haut['code_crue'] == from_year]
    last_year = gdp_df_haut[gdp_df_haut['code_crue'] == to_year]
    # -----------------------------------------------------------------------------

    # Filter the dataframe based on the widget input and reshape it.
    df_filtered_haut = gdp_df_haut[(gdp_df_haut["code_station"].isin(selected_station)) & (gdp_df_haut["code_crue"].between(from_year, to_year))]
    df_reshaped_haut = df_filtered_haut.pivot_table(
        index="code_crue", columns="code_station", values="value", aggfunc="sum", fill_value=0
    )

    #Filter données de la crue 2022 car sinon que 2000 qui est incomplet car non présent pour la Garonne
    df_filtered_haut = df_filtered_haut.query("code_crue == 2022")
    df_filtered_haut['value'] = df_filtered_haut['value']/1000
    df_filtered_haut = df_filtered_haut.query("libelle_cours_eau != 'Le Grand Hers'")
    df_filtered_haut = df_filtered_haut.query("libelle_cours_eau != 'La Louge'") #df_filtered_haut[df_filtered_haut["libelle_cours_eau"].apply(lambda x: 'La Louge' not in x)]

    df_filtered_haut = df_filtered_haut.sort_values(by=['code_crue', 'surface_bassin_versant','altitude_site'], ascending=False)

    fig1 = px.line(df_filtered_haut[df_filtered_haut["code_station"].apply(lambda x: 'O200001001' not in x)] , y="value", x="date_m_d", color="code_crue",color_discrete_sequence=px.colors.sequential.gray, facet_row='libelle_cours_eau' ,  category_orders={"libelle_cours_eau": ["Le Grand Hers", "L'Ariège", "Le Salat", "La Louge"],  "code_crue": ["2022", "2000", "1977", "1952", "1905"] }, #gray
        ) #width = 1300, height = 600,.update_traces(side="positive", width=1)#, "time": ["Lunch", "Dinner"] box=True, points="altitude_site") #hover_data=filtered_gdp_df_debit.code_crue,
    fig1.update_yaxes(visible=True, showgrid =False, showticklabels=True)
    fig1.update_xaxes(
    dtick="M1",
    tickformat="%b")


    #fig1.add_vrect( # ou vline pour verticale avec x=...
    #          x0="2022-01-10", x1="2022-01-12", line_dash="dot")
    ''
    fig1.add_trace(px.line(df_filtered_haut.query("code_station == 'O200001001'"), y="value", x="date_m_d", color="code_crue", color_discrete_sequence=px.colors.sequential.gray, facet_col='libelle_cours_eau' ).data[0])
    
    fig1.add_vrect( x0="2022-01-10", x1="2022-01-12",
                   col=1, # numéro de la colonne (les figures de droites)
                   #annotation_text="2022",
                   #annotation_position="top left",
                   fillcolor="#009CDD", opacity=0.2, line_width=0.1) # ou vline pour verticale avec x=...x=1, line_dash="dot",annotation_text="11 janvier 2022",annotation_position="bottom right")
   
    #fig1.update_layout(yaxis_title=True)
    fig1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    fig1.for_each_trace(lambda t: t.update(name=t.name.split("=")[0]))       
    fig1.update_layout(xaxis_title=None)
    fig1.update_layout(showlegend=True)
    st.plotly_chart(fig1)



    # Display the data as a table using `st.dataframe`.
    st.dataframe(
        df_filtered_haut,
        use_container_width=True,
        column_config={"code_crue": st.column_config.TextColumn("code crue")},
    )

with tab3:
    st.header("Pluviométrie", divider='gray')
    st.caption("Des pluies abondantes dans les Pyrénées. :ocean: :mountain: :cloud:  :snowflake: ")

    # Filter station
    station_pluv = gdp_df_pluv['code_pluviometre'].unique()
    if not len(station_pluv):
        st.warning("Selectionner au moins une station")

    selected_station_pluv = st.sidebar.multiselect('Quelle station de pluviométrie souhaitez-vous regarder ?', station_pluv,  ['31135001','31517001','31190001','31144001','31085400','31085400'])

    df_filtered_pluv = gdp_df_pluv[(gdp_df_pluv["code_pluviometre"].isin(selected_station_pluv)) & (gdp_df_haut["code_crue"].between(from_year, to_year))]

    fig_pluv0 = px.line(df_filtered_pluv.query("code_pluviometre == '31135001'"), y="precipitation", x="date_m_d", color="code_crue", hover_data=['code_crue'])
    fig_pluv0.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    fig_pluv0.for_each_trace(lambda t: t.update(name=t.name.split("=")[0]))       
    fig_pluv0.update_layout(xaxis_title=None)
    fig_pluv0.update_layout(showlegend=True)
    st.plotly_chart(fig_pluv0)

    fig_pluv2 = px.scatter_mapbox(gdp_df_pluv.query("precipitation>0").query("code_crue==2022"), lat="latitude", lon="longitude", color="precipitation", size="precipitation", 
                            title = "9 janvier : J-2 avant la crue du 11 janvier 2022 de fortes précipitations", color_continuous_scale='teal',
                            #radius=200, #["orange", "blue"],  #.query("date_prod_year>1000") colors.cyclical.IceFire color="puiss_total_elec", size="puiss_total_elec", color_continuous_scale=["blue", "red"],
                            hover_data=['date_observation'], #labels={'code_station'},
                            opacity = 1, size_max=60, zoom=7.5,
                            mapbox_style="carto-positron",text="code_pluviometre",
                            animation_frame="date_m_d",
                            width=100, height=700, #pitch=60, bearing=180,
                            range_color=[0, 253] ) #,range_color=[0, 3830137]
    #fig_pluv2.update_layout(#margin={"r":0,"t":0,"l":0,"b":0}, 
    #              mapbox=dict(
    #                  #pitch=60,
    #                  bearing=180
    #              ))

    st.plotly_chart(fig_pluv2)
    #fig.show()
    
    #['code_pluviometre','code_crue','date_observation'],
    #    'precipitation'
    #get_data_pluv = get_data_pluv.sort_values(by=['code_pluviometre', 'precipitation','code_crue'], ascending=False)
    #st.plotly_chart(fig_pluv)

    #import plotly.express as px
    #import numpy
    #from plotly_calplot import calplot
    # choosing a standard colorscale
    fig_pluv1 = calplot(
        df_filtered_pluv.query("code_pluviometre == '31135001'"),
        x="date_observation",
        y="precipitation",
        gap=0,
        colorscale="blues", # standard is greens
        dark_theme=False,
        years_title=True,
        #name="Data",
        month_lines_width=3,
        title = 'Précipitation code pluviometre : 31157001',
        #suptitle='lorem ipsum',
        #cmap='Spectral_r',
        #facet_row="code_pluviometre"
        #month_lines_color="#fff"
    )
    st.plotly_chart(fig_pluv1)

    df_filtered_pluv

with tab4:
    st.write('''S'ambiancer''')
    # 🎵 ⛰️ Add a video with my favorite music that have a relation with the mountain (or juste the sound) 
    #"https://www.youtube.com/watch?v=t51_2ZEyuj4&pp=ygUKI2FubmFsZW9uZQ%3D%3D" "https://soundcloud.com/annaleone/still-i-wait?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
    #"https://soundcloud.com/annaleone/sets/still-i-wait?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing" "https://soundcloud.com/ocie-elliott/wait-for-you?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
    #"https://soundcloud.com/indiefolkcentral/ocie-elliott-down-by-the-water?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing" "https://soundcloud.com/dominika-zolnierczuk/sets/ocie-elliott?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
    video_url = "https://soundcloud.com/ocie-elliott/like-a-river?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
    st_player(video_url) #, subtitles="subtitles.vtt" subtitles="subtitles.vtt"Interessant d'avoir le texte qui défile ! 

    #st.markdown(":gray-badge[+4°C en 2100]  Trajectoire de réchauffement de référence pour l’adaptation au changement climatique (TRACC)")

    #st.markdown("   :red-badge[🌨️ +15 %] les pluies intenses à prévoir, aggravant le risque d'inondation")
    #st.markdown("   :orange-badge[🌡️ +1,5 °C] c'est la variation de la température moyenne enregistrée en 50 ans sur les Pyrénées (Source : Observatoire pyrénéen du changement climatique)")
    #st.markdown("   :orange-badge[🌄 1/2] les glaciers pyrénéens la moitié d’entre eux ont disparu ces 35 dernières années. Le stock de neige faiblira drastiquement au printemps dans les Pyrénées dans le scénario")


#data
#DATA_FILENAME = Path(__file__).parent/'data/station.geoparquet'
#raw_station_df = gpd.read_parquet(DATA_FILENAME)

#in_geoparquet = "station.geoparquet"
#listings_df = gpd.read_geoparquet(in_geoparquet)


#st.pydeck_chart(
#    pdk.Deck(
#        map_style=f"{mapstyle}",
#        initial_view_state=pdk.ViewState(
#        latitude=43.29966,
#        longitude=1.36743,
#        zoom=9,pitch=60,bearing=190 
#        ),
#        layers=[
#            pdk.Layer(
#                "ScatterplotLayer",
#                data=gdp_df_station,
#                get_position=["st_y", "st_x",],
#                get_color=[200,20,20],
#                get_radius=120
#            )
#        ],))
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

