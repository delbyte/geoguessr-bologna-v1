import numpy as np
from shapely.geometry import LineString, Point
import osmnx as ox
import pandas as pd
import folium

city = "Bologna, Italy"

G = ox.graph_from_place(city, network_type="drive")

edges = ox.graph_to_gdfs(G, nodes=False)

spacing = 10

def interpolate_points(road, spacing):
    length = road.length
    num_points = int(length//spacing)
    if num_points <1:
        return []
    return [road.interpolate(d) for d in np.linspace(0, length, num_points)]

all_points = []
for road in edges.geometry:
    if isinstance(road, LineString):
        all_points.extend(interpolate_points(road, spacing))

coords = [(point.y, point.x) for point in all_points]


#TODO - NEED TO CHECK IF STREETVIEW IS AVAILABLE ON MAPILLARY FOR GENERATED COORDS from coords
df = pd.DataFrame(coords, columns=["latitude", "longitude"]).to_csv("bologna_streetview_coords.csv", index =False)


#FOR TESTING 