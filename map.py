#source activate ox

from flask import Flask, render_template,request
import osmnx as ox
import pickle
import numpy as np
import networkx as nx
import requests
import geopandas as gpd
from folium.map import *
from folium import plugins
from folium.plugins import MeasureControl
from sklearn.neighbors import KDTree
import folium
import matplotlib.pyplot as plt
import ogr
import os
from pyproj import Proj, transform
import json
import requests
from flask import Flask, render_template, url_for, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo



# def finding_nearest_shelter(houses,shelters):
#     max_house=len(houses)//len(shelters)
#     for shelter in shelters:
#         for house in houses:
#



def display_flooded_homes(houses,m):
    for house in houses:
        folium.Marker(location=house,icon=folium.Icon(color='red')).add_to(m)
    return m

def display_shelter_homes(shelters,m):
    i=1
    for shelter in shelters:
        popup=i
        i+=1
        folium.Marker(location=shelter,icon=folium.Icon(color='green'),popup=popup).add_to(m)
    return m

def find_paths(source,target,m):
    node1=ox.geo_utils.get_nearest_node(G, source, method='haversine', return_dist=False)
    node2=ox.geo_utils.get_nearest_node(G, target, method='haversine', return_dist=False)
    route=nx.shortest_path(G, node1,node2)
    print(route)
    m = ox.plot_route_folium(G, route, route_color='green')
    folium.Marker(location=source,icon=folium.Icon(color='red')).add_to(m)
    folium.Marker(location=target,icon=folium.Icon(color='red')).add_to(m)
    return m

def find_all_paths(source,target,m):
    node1=ox.geo_utils.get_nearest_node(G, source, method='haversine', return_dist=False)
    node2=ox.geo_utils.get_nearest_node(G, target, method='haversine', return_dist=False)
    routes=nx.all_shortest_paths(G, source, target, weight=None)
    print(routes)
    # m = ox.plot_route_folium(G, routes[0], route_color='green')
    folium.Marker(location=source,icon=folium.Icon(color='red')).add_to(m)
    folium.Marker(location=target,icon=folium.Icon(color='red')).add_to(m)
    return m

def convert_cord_sys(cord):
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:32643')
    x1,y1 = cord[0],cord[1]
    x2,y2 = transform(inProj,outProj,x1,y1)
    return [x2,y2]

def find_nodes():
    shelter_locations = gpd.read_file('shape_files/SH.shp')
    house_locations = gpd.read_file('shape_files/Hospitals_selected.shp')
    houses=[]
    shelters=[]
    # print(shelter_locations.NAME)
    for shelter_location in shelter_locations.geometry:
        point=[float(str(shelter_location).split('(')[1].split(' ')[1].split(')')[0]),float(str(shelter_location).split('(')[1].split(' ')[0])]
        shelters.append(point)
    # print(houses)
    for house_location in house_locations.geometry:
        point=[float(str(house_location).split('(')[1].split(' ')[1].split(')')[0]),float(str(house_location).split('(')[1].split(' ')[0])]
        houses.append(point)
    # print(houses)
    return np.array(houses),np.array(shelters)


############################################################main############################
view_flag=1
houses,shelters=find_nodes()


dbfile = open('thrissurPickle', 'rb')
G= pickle.load(dbfile)
# G=ox.graph_from_bbox(10.7157, 10.6527, 76.4712, 76.3808, network_type='all_private', simplify=True)


class Button(FlaskForm):
    shelter_btn = SubmitField('Shelter Homes')
    house_btn = SubmitField('Flooded houses')
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


@app.route("/")
@app.route("/home")
def home():
    return render_template('first.html')
@app.route("/map", methods=['GET', 'POST'])
def register():
    global view_flag
    m = folium.Map(location=[ 10.6857231, 76.4203169 ],width='50%', height='80%')
    m.save('templates/map.html')
    form = Button()
    if form.validate_on_submit():
        print(form.shelter_btn.data)
        if form.shelter_btn.data==True :

            if view_flag==1:
                print('shelter')
                m=display_shelter_homes(shelters,m)
                m.save('templates/map.html')
                view_flag=0
            else:
                m = folium.Map(location=[ 10.6857231, 76.4203169 ],width='50%', height='80%')
                m.save('templates/map.html')
                view_flag=1

        if form.house_btn.data==True:
            if view_flag==1:
                button=2
                print('house')
                m=display_flooded_homes(houses,m)
                m.save('templates/map.html')
                view_flag=0
            else:
                m = folium.Map(location=[ 10.6857231, 76.4203169 ],width='50%', height='80%')
                m.save('templates/map.html')
                view_flag=1
    return render_template('home.html', title='map', form=form)




if __name__ == '__main__':
    app.run(debug=True)



# source=houses[10]
# target=shelters[0]
# m=find_paths(source,target,m)
# m=display_flooded_homes(houses,m)
# m=display_shelter_homes(shelters,m)
