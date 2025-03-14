import numpy as np
from shapely.geometry import LineString, Point
import osmnx as ox
import pandas as pd
import folium
import webbrowser

city = "Bologna, Italy"

G = ox.graph_from_place(city, network_type="drive")

ox.plot_graph(G)


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

print(edges.head())
print(len(edges))


#TODO - NEED TO CHECK IF STREETVIEW IS AVAILABLE ON MAPILLARY FOR GENERATED COORDS from coords
df = pd.DataFrame(coords, columns=["latitude", "longitude"]).to_csv("bologna_streetview_coords.csv", index =False)


#FOR TESTING 
# Compute the average latitude and longitude of all valid points
if coords:
    avg_lat = sum(lat for lat, lon in coords) / len(coords)
    avg_lon = sum(lon for lat, lon in coords) / len(coords)
    map_center = [avg_lat, avg_lon]
else:
    map_center = [44.4949, 11.3426]  # Fallback to Bologna center if no points exist

m = folium.Map(location=map_center, zoom_start=13)

for lat, lon in coords:
    folium.CircleMarker([lat, lon], radius=15, color="pink", fill=True).add_to(m)

print(coords)

m.save("bologna_map.html")
webbrowser.open("bologna_map.html")