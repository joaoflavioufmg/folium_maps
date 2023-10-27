# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# https://colab.research.google.com/drive/19MW7waz_SAC1IMO3PCuFF2LrWOHyF9C7?usp
# https://www.ibge.gov.br/explica/codigos-dos-municipios.php
# https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html?=&t=acesso-ao-produto
# https://servicodados.ibge.gov.br/api/docs/malhas?versao=3
# https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{id}
# https://servicodados.ibge.gov.br/api/docs/malhas?versao=3#api-Metadados-municipiosIdMetadadosGet
# https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=maxima&intrarregiao=municipio

import sys  # Importa modulos do sistema
import os
import csv
import json
import openpyxl
import branca.colormap as cm
import haversine as hs
import networkx as nx


import pandas as pd
import folium
from folium.features import DivIcon
import math
import io
import requests
import webbrowser
# import matplotlib.pyplot as plt

print('Vesão do python: ', sys.version)  # Versao do python em uso
firefox = webbrowser.Mozilla("C:\\Program Files\\Mozilla Firefox\\firefox.exe")

mapa_brasil = folium.Map(location=[-22.7864889,-50.6786708],zoom_start=4)

# ########################## # Rodar apenas na primeira vez. (Escolha entre resolucao maxima, media, ou minima) ##############################
# # url = 'https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=maxima&intrarregiao=municipio'
# # url = 'https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=intermediaria&intrarregiao=municipio'
# url = 'https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=municipio'
# headers = {'Accept': 'application/json'}
# r = requests.get(url, headers=headers)
# data = r.json()
# with open('br_municipios.json', 'w') as f:
#   json.dump(data, f)
# #############################################################################################################################################

# https://servicodados.ibge.gov.br/api/docs/malhas?versao=3
f1 = open('br_municipios_min.json')
f2 = open('br_estados_min.json')
# f = open('br_municipios.json')

municipios_json = json.load(f1)
estados_json = json.load(f2)
# print("municipios_json: ", municipios_json)
# folium.GeoJson(municipios_json).add_to(mapa_brasil)

# mapa_brasil.save('br_map.html')
# firefox.open('file://' + os.path.realpath('br_map.html'))

# df = pd.read_excel('./BRmun_dados.xlsx', sheet_name='MUN', skiprows=[0], index_col='None', skipfooter=1)
df = pd.read_csv('./BRmun_dados.csv', encoding ='latin-1')
# df = pd.read_csv('./BRmun_dados.csv', encoding ="utf-8")
# print("df: ", df)

# Os códigos serãp armazenados no índice como string para depois
# utilizar em conjunto com o campo com os dados georeferenciados.
df.code=(df.origin2).apply(str)
df.index=df.code
print("df: ", df)


# Inserção de dados de produção nos dados georeferenciados
index = df.index
# print("index: ", index)

for mun in municipios_json['features']:
  # Converter de string para número (usado no índice da tabela com dem, infr e num_em).
#   print("mun: ", mun)
  codarea = mun['properties']['codarea']
  # print("codarea: ", codarea)
  # Busca do código de área no índice da linha da Tabela.
  if codarea in index:
    #print(df.loc[codarea,'dem'])
    mun['properties']['mun2'] = df.loc[codarea,'mun2']
    mun['properties']['pop'] = float(df.loc[codarea,'pop'])
    mun['properties']['dem'] = float(df.loc[codarea,'dem'])
    mun['properties']['infr'] = float(df.loc[codarea,'infr'])
    mun['properties']['num_em'] = float(df.loc[codarea,'num_em'])
  else:
    mun['properties']['mun2'] = ""
    mun['properties']['pop'] = 0.0
    mun['properties']['dem'] = 0.0
    mun['properties']['infr'] = 0.0
    mun['properties']['num_em'] = 0.0
  
# print("municipios_json['features'][1]: ", 
#     municipios_json['features'][1])
# print("municipios_json['features'][1]['properties']: ", 
#     municipios_json['features'][1]['properties'])
# print("municipios_json['features'][1]['properties']['dem']: ", 
#     municipios_json['features'][1]['properties']['dem'])
  
# print("municipios_json: ", municipios_json)
# print("municipios_json['features'][1]['properties']['dem']: ", 
#       municipios_json['features'][1]['properties']['dem'])
# print("municipios_json['features'][1]['properties']['infr']: ", 
#       municipios_json['features'][1]['properties']['infr'])
# print("municipios_json['features'][1]['properties']['num_em']: ", 
#       municipios_json['features'][1]['properties']['num_em'])

# print("type(municipios_json['features'][1]['properties']['codarea']): ", 
#     type(municipios_json['features'][1]['properties']['codarea']))
# print("type(df.index[0]): ", type(df.index[0]))
# print("type(df.code[0]): ", type(df.code[0]))
# print("municipios_json: ", municipios_json)

# # ========= Rodar apenas um vez para criar o arquivo ==============
# with open("municipios.json", "w") as outfile:
#     json.dump(municipios_json, outfile)
# # =================================================================

hubs_infr_temp = df.loc[df['infr'] == 1]
hubs_infr = hubs_infr_temp.reset_index(drop=True)
hubs_infr.columns = ['origin', 'codigo_ibge', 'lat', 'lng', 'pop', 'dem', 'infr', 'num_em', 'capacity', 'mun', 'nome']
hubs_infr.drop('origin', inplace=True, axis=1)
hubs_infr.drop('codigo_ibge', inplace=True, axis=1)
hubs_infr.drop('lat', inplace=True, axis=1)
hubs_infr.drop('lng', inplace=True, axis=1)
hubs_infr.drop('pop', inplace=True, axis=1)
hubs_infr.drop('dem', inplace=True, axis=1)
hubs_infr.drop('infr', inplace=True, axis=1)
hubs_infr.drop('num_em', inplace=True, axis=1)
hubs_infr.drop('capacity', inplace=True, axis=1)
hubs_infr.drop('mun', inplace=True, axis=1)
# print("hubs_infr: ", hubs_infr) # 65 cidades

hubs_em_temp = df.loc[df['num_em'] >= 1]
hubs_em = hubs_em_temp.reset_index(drop=True)
hubs_em.columns = ['origin', 'codigo_ibge', 'lat', 'lng', 'pop', 'dem', 'infr', 'num_em', 'capacity', 'mun', 'nome']
hubs_em.drop('origin', inplace=True, axis=1)
hubs_em.drop('codigo_ibge', inplace=True, axis=1)
hubs_em.drop('lat', inplace=True, axis=1)
hubs_em.drop('lng', inplace=True, axis=1)
hubs_em.drop('pop', inplace=True, axis=1)
hubs_em.drop('dem', inplace=True, axis=1)
hubs_em.drop('infr', inplace=True, axis=1)
hubs_em.drop('num_em', inplace=True, axis=1)
hubs_em.drop('capacity', inplace=True, axis=1)
hubs_em.drop('mun', inplace=True, axis=1)
# print("hubs_em: ", hubs_em) # 5 cidades

# url = 'https://github.com/kelvins/Municipios-Brasileiros/blob/master/csv/municipios.csv'
# # Executando protocolo para a requisição de dados contidos em um arquivo .csv na internet.
# s=requests.get(url).content
# file_name = io.StringIO(s.decode('utf-8'))
# lat_long = pd.read_html(file_name)

lat_lng_df = pd.read_csv('./municipios_latlng.csv', encoding = "utf-8")
lat_lng_df.drop('siafi_id', inplace=True, axis=1)
lat_lng_df.drop('ddd', inplace=True, axis=1)
lat_lng_df.drop('fuso_horario', inplace=True, axis=1)
# print("lat_lng_df: ", lat_lng_df)


hubs_infr_lat_lng = pd.merge(left=hubs_infr, right=lat_lng_df, 
                             left_on='nome', right_on='nome', how='inner')
hubs_infr_lat_lng.drop_duplicates(subset ="nome", keep = "first", inplace = True) 
hubs_infr_lat_lng.reset_index(drop=True, inplace=True)
# print("hubs_infr_lat_lng: ", hubs_infr_lat_lng)


hubs_em_lat_lng = pd.merge(left=hubs_em, right=lat_lng_df, 
                             left_on='nome', right_on='nome', how='inner')
hubs_em_lat_lng.drop_duplicates(subset ="nome", keep = "first", inplace = True) 
hubs_em_lat_lng.reset_index(drop=True, inplace=True)
# print("hubs_em_lat_lng: ", hubs_em_lat_lng)

hubs_em_lat_lng['codigo_ibge'] = hubs_em_lat_lng['codigo_ibge'].astype('int')
# print(type(hubs_em_lat_lng['codigo_ibge'][0]))

supply_temp = df.copy()
supply_temp = supply_temp.loc[df['infr'] == 1]
supply = supply_temp.reset_index(drop=True)
supply.columns = ['origin', 'codigo_ibge', 'lat', 'lng', 'pop', 'dem', 'infr', 'num_em', 'capacity', 'mun', 'nome']
supply.drop('origin', inplace=True, axis=1)
supply.drop('lat', inplace=True, axis=1)
supply.drop('lng', inplace=True, axis=1)
supply.drop('pop', inplace=True, axis=1)
supply.drop('dem', inplace=True, axis=1)
supply.drop('capacity', inplace=True, axis=1)
supply.drop('mun', inplace=True, axis=1)
supply.drop('nome', inplace=True, axis=1)
supply['codigo_ibge'] = supply['codigo_ibge'].astype('int')

supply_lat_lng = pd.merge(left=supply, right=lat_lng_df, 
                             left_on='codigo_ibge', right_on='codigo_ibge', how='inner')
supply_lat_lng.drop_duplicates(subset ="codigo_ibge", keep = "first", inplace = True) 
supply_lat_lng.reset_index(drop=True, inplace=True)
supply_lat_lng = supply_lat_lng.reset_index(drop=True)
print("supply_lat_lng: ", supply_lat_lng)


demand = df.copy()
demand.columns = ['origin', 'codigo_ibge', 'lat', 'lng', 'pop', 'dem', 'infr', 'num_em', 'capacity', 'mun', 'nome']
demand.drop('origin', inplace=True, axis=1)
demand.drop('lat', inplace=True, axis=1)
demand.drop('lng', inplace=True, axis=1)
demand.drop('pop', inplace=True, axis=1)
demand.drop('capacity', inplace=True, axis=1)
demand.drop('mun', inplace=True, axis=1)
demand.drop('nome', inplace=True, axis=1)
demand['codigo_ibge'] = demand['codigo_ibge'].astype('int')

demand_lat_lng = pd.merge(left=demand, right=lat_lng_df, 
                             left_on='codigo_ibge', right_on='codigo_ibge', how='inner')
demand_lat_lng.drop_duplicates(subset ="codigo_ibge", keep = "first", inplace = True) 
demand_lat_lng.reset_index(drop=True, inplace=True)
demand_lat_lng = demand_lat_lng.reset_index(drop=True)
print("demand_lat_lng: ", demand_lat_lng)

dist_dur = pd.read_csv('./BR_dist_dur.csv', encoding = "utf-8")
# dist_dur.columns = ['codigo_ibge','codigo_ibge','km','seconds']
print("dist_dur: ", dist_dur)

# def distancia(origin, dest):
#   D = []
#   for o in range(len(origin)):
#     aux = []
#     for d in range(len(dest)):
#       dist = hs.haversine(origin.iloc[o,:],dest.iloc[d,:])
#       aux.append(dist)
#     D.append(dist)
#   return D

# # print("distancia(origin, dest): ", distancia(1100015, 1100205))
# origin  = demand_lat_lng[['latitude', 'longitude']]
# dest = supply_lat_lng[['latitude', 'longitude']]
# D = distancia(origin, dest)
# incosts = D
# # print(D)

# https://stackoverflow.com/questions/33282119/pandas-filter-dataframe-by-another-dataframe-by-row-elements
dest = supply.copy()
dest.columns = ['dest', 'infr', 'num_em']
dest.drop('infr', inplace=True, axis=1)
dest.drop('num_em', inplace=True, axis=1)
# print("dest: ", dest)
keys = list(dest.columns.values)
# print("keys: ", keys)
i1 = dist_dur.set_index(keys).index
# print("i1: ", i1)
i2 = dest.set_index(keys).index
# print("i2: ", i2)
D_temp = dist_dur[i1.isin(i2)]
D1 = D_temp.reset_index(drop=True)
D1.drop('km', inplace=True, axis=1)
print("D1: ", D1)
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.pivot.html
# D = D1.pivot(index='origin', columns='dest')['seconds']
# print("D: ", D)



####################### ... ou Distancia Circular #################################
# ori_dest = dist_dur
# G = nx.from_pandas_edgelist(dist_dur, source='origin', target='dest', 
#                             edge_attr='seconds', create_using=nx.MultiDiGraph)
# out = [list(nx.get_edge_attributes(G.subgraph({n}|nx.descendants(G, n)),
#                                    'seconds').values()) 
#                                    for n in dist_dur['origin'].unique()]
# s = pd.Series(out, index=dist_dur['origin'].unique())
# final = (dist_dur.assign(link=dist_dur['origin'].map(s)).explode('dest')
#          .pivot_table(index='origin', columns='dest', values='seconds',
#                       aggfunc=list))
# print("final: ", final)
###################################################################################

##############################
# > Solucao da otimizacao ...
##############################
# Ex: tabela ficticia importada...
# solution = D1.head(100)
# solution.to_csv('solution.csv')
df_flow = pd.read_csv('./solution.csv', encoding = "utf-8")
# final_producao = pd.merge(left = dfs_final, right = df2, left_on='CÓDIGO', right_on='codigo_ibge', how='inner')
print("df_flow: ", df_flow)

origin = df_flow.copy()
destination = df_flow.copy()
origin.columns = ['item','origin','latitude','longitude','seconds','dest','lat','long']
origin.drop('item', inplace=True, axis=1)
origin.drop('seconds', inplace=True, axis=1)
origin.drop('dest', inplace=True, axis=1)
origin.drop('lat', inplace=True, axis=1)
origin.drop('long', inplace=True, axis=1)
df_cod_mum = pd.read_csv('./br_municipios.csv', encoding='latin-1')
# df_cod_mum = pd.read_csv('./br_municipios.csv', encoding='utf-8')
origin = pd.merge(left=origin, right=df_cod_mum, left_on='origin',
                  right_on='codigo', how='inner')
origin.drop('codigo', inplace=True, axis=1)
origin = origin[['origin','nome','latitude','longitude']]
print("origin: ", origin)

destination.columns = ['item','origin','latitude','longitude','seconds','dest','lat','long']
destination.drop('item', inplace=True, axis=1)
destination.drop('origin', inplace=True, axis=1)
destination.drop('latitude', inplace=True, axis=1)
destination.drop('longitude', inplace=True, axis=1)
destination.drop('seconds', inplace=True, axis=1)
destination.columns = ['dest','latitude','longitude']
destination = pd.merge(left=destination, right=df_cod_mum, left_on='dest',
                  right_on='codigo', how='inner')
destination.drop('codigo', inplace=True, axis=1)
destination = destination[['dest','nome','latitude','longitude']]
print("destination: ", destination)

# Construindo os gráficos de fluxo de soja da forma correta: primeiro os nós da rede e 
# depois os fluxos entre eles. Observar que com isso é possível realizar a separação 
# entre os nós de produção, hub, portos e destinos finais através de 4 cores. 
# Também é possível criar classes de nós e agrupar em grupos diferentes de modo 
# a permitir que apenas uma parte da rede seja visualizada. Os nós podem ser 
# associados aos nomes das cidades e números utilizados na descrição topológica da rede. 
# Os fluxos podem ser clicados e irá aparecer o fluxo correspondente, bem como sua 
# espessura é determinada como uma proporção do logarítmo do fluxo. 
# O logarítmo foi utilizada devida à diferença dos valores de fluxo variar em mais 
# de duas ordens de escala. Como apenas os fluxos x serão desenhados, então, apenas 
# uma cor, a mesma cor empregada para desenhar os nós de produção, será empregada.



# dem_scale = (df['dem'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()
dem_scale = (df['dem'].quantile((0.3,0.6,0.9))).tolist()
print("dem_scale: ", dem_scale)
# supply_scale = (df['pop'].quantile((0.0,0.1,1.0))).tolist()
supply_scale = [0,1,2,3,4,5]
print("supply_scale: ", supply_scale)

# https://python-visualization.github.io/folium/latest/advanced_guide/colormaps.html

print("estados_json: ", estados_json['features'][0]['properties']['codarea'])

def my_color_function(feature):
    """Maps low values to green and high values to red."""    
    if int(estados_json['features'][0]['properties']['codarea']) > 0:
        return " #FFFFFF"
    else:
        return " #000000"
    
# colormap = cm.LinearColormap(colors=['blue','green','yellow','orange','red','purple'], index=dem_scale,vmin=0.0,vmax=max(dem_scale))
# colormap = cm.LinearColormap(["red", "orange", "yellow", "green"], index=[0, 1000, 10000, 170947],vmin=0.0,vmax=max(dem_scale))
# colormap = cm.LinearColormap(["green", "yellow", "red"], index=[0, 1000, 170947],vmin=0.0,vmax=max(dem_scale))
# colormap = cm.LinearColormap(["green", "yellow", "red"], index=dem_scale,vmin=0.0,vmax=max(dem_scale))
colormap = cm.LinearColormap(["red", "yellow", "green"], index=dem_scale,vmin=min(dem_scale),vmax=max(dem_scale))
colormap.caption = 'Demand'     #Caption for legend
# linear = cm.LinearColormap(['green','yellow','red'], vmin=6, vmax=170947)
# colorscale = cm.linear.RdYlBu_11.to_step(6).scale(0, 170947)
colorscale = cm.step.RdYlBu_11.to_linear().scale(vmin=min(supply_scale),vmax=max(supply_scale))
# colorscale = cm.step.RdYlBu_11.to_linear().scale(index=dem_scale, vmin=0.0,vmax=max(dem_scale))
colorscale.caption = 'Supply'     #Caption for legend
# print("colormap: ", colormap)
# plt(colormap)

states = folium.FeatureGroup(name='States')
states.add_child(folium.GeoJson(data=estados_json,
                                # style_function = lambda feature:{
                                style_function = lambda x:{
                                # 'fillColor':my_color_function(feature),                                
                                'color':'black', #border color for the color fills
                                'weight': 2, #how thick the border has to be
                                'opacity':1,
                                'fillOpacity':0.2,
                                'interactive':False}))

fgp = folium.FeatureGroup(name='Demand')

tooltip=folium.features.GeoJsonTooltip(
        # fields=['codarea','dem'],
        fields=['mun2','dem'],        
        aliases=['Municipality: ','Demand'],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
)

fgp.add_child(folium.GeoJson(data=municipios_json,
                             tooltip=tooltip,                            
                            #  style_function = lambda x:{'fillColor':colormap(x['properties']['dem']),
                            #                           'fillcolor':'#black','fillOpacity':0.8,'weight':0.8}))
                            #  style_function=style_function))
                             style_function = lambda feature:{'fillColor':colormap(feature['properties']['dem']),
                                                        'color':'black', #border color for the color fills
                                                        'weight': 0.6, #how thick the border has to be
                                                        'fillOpacity':0.8}))

# print("df: ", df)

# https://medium.com/data-hackers/criando-mapas-interativos-e-choropleth-maps-com-folium-em-python-abffae63bbd6
cp = folium.Choropleth(data=df,                       
                       geo_data=municipios_json,
                       columns=['origin2','num_em'],  # Coluna 1 "origin2" == coluna "feature.properties.codarea"
                       key_on="feature.properties.codarea",                      
                      #  fill_color='YlGnBu', 
                      #  fill_color='YlOrRd',
                      #  fill_color="YlGn",  
                      # fill_color='BuGn', 
                      fill_color='BuPu', 
                      # fill_color='GnBu', 
                      # fill_color='OrRd' 
                      # fill_color='PuBu', 
                      # fill_color='PuBuGn', 
                      # fill_color='PuRd', 
                      # fill_color='RdPu', 
                      # fill_color='YlGn', 
                      # fill_color='YlGnBu', 
                      # fill_color='YlOrBr'.
                       fill_opacity=1.0,
                       line_opacity=0.7,
                       smooth_factor=0,                            
                       line_color='black',
                       highlight=True,
                       name='Supply',
                       threshold_scale=supply_scale,
                       legend_name='Supply',
                      #  show=False,
                       overlay=True,
                       nan_fill_color = "White"
                       )

# https://stackoverflow.com/questions/70471888/text-as-tooltip-popup-or-labels-in-folium-choropleth-geojson-polygons
folium.GeoJsonTooltip(
  fields=['mun2','num_em'],        
  aliases=['Municipality: ','Supply'],
  style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
).add_to(cp.geojson)


mapa_brasil.add_child(cp)
# mapa_brasil.add_child(colorscale)
mapa_brasil.add_child(colormap)
mapa_brasil.add_child(fgp)
mapa_brasil.add_child(states)

def draw_nodes(df_nodes, color, fg):
  # Drawing origin nodes.
  for index,row in df_nodes.iterrows():
    # number = index + 1
    number = ""
    pop  = '<head><meta http-equiv="Content-Type" content="text/html; charset=windows-1252"></head>'
    pop += row['nome']
    # pop = (row['nome']).encode('latin-1')    
    xlat = row['latitude']
    xlon = row['longitude']
    col = color
    fg = fg
  
    folium.CircleMarker(location=[xlat, xlon], radius=10, 
                        color=col, fill=True, fill_color=col).add_to(fg)

    folium.Marker(location=[xlat, xlon], popup = pop, icon=DivIcon(icon_size=(150,36), 
                                                                   icon_anchor=(10,30),
          html='<b><div style="font-size: 11pt; color : {}">{}</div></b>'.format(col, 
                                                                          number))).add_to(fg)


def draw_branches(df_flow, color, fg):
  # Drawing branches.
  for index,row in df_flow.iterrows():
    xlat  = row['latitude']
    xlon  = row['longitude']
    ylat  = row['lat']
    ylon  = row['long']
    text = round(float(row['seconds']/3600),2)
    stext = str(text) + "(h)"
    nflow = float(text)/1000
    nflow = math.log(nflow)
    folium.PolyLine([[xlat, xlon], [ylat, ylon]], weight=(nflow), 
                    color=color, popup=stext).add_to(fg)

fg1 = folium.FeatureGroup(name = "Origin")
fg2 = folium.FeatureGroup(name = "Destination")
fg3 = folium.FeatureGroup(name = "Flow")

# Drawing origin and destination nodes.
draw_nodes(origin, '#080808', fg1)
draw_nodes(destination, ' #020385', fg2)
# Draw flow branches.
draw_branches(df_flow, '#080808', fg3)
  
  
mapa_brasil.add_child(fg1)
mapa_brasil.add_child(fg2)
mapa_brasil.add_child(fg3)
mapa_brasil.add_child(folium.LayerControl())

mapa_brasil.save('br_map.html')
firefox.open('file://' + os.path.realpath('br_map.html'))
