import numpy as np
from shapely.geometry import LineString, Point
import osmnx as ox
import geopandas as gpd
import pandas as pd
import folium
import webbrowser

city = "Bologna, Italy"

# Get road network in lat/lon (WGS84)
G = ox.graph_from_place(city, network_type="drive")

# Convert to GeoDataFrame
edges = ox.graph_to_gdfs(G, nodes=False)

# Project to UTM (meters) for correct distance calculations
edges = edges.to_crs(epsg=32632)  # UTM Zone for Bologna

spacing = 10  # Spacing in meters

def interpolate_points(road, spacing):
    """Generate interpolated points along a road with given spacing."""
    length = road.length  # Length in meters
    num_points = max(1, int(length // spacing))  # At least 1 point per road
    return [road.interpolate(d) for d in np.linspace(0, length, num_points)]

# Generate interpolated points
all_points = []
for road in edges.geometry:
    if isinstance(road, LineString):
        all_points.extend(interpolate_points(road, spacing))

# Convert interpolated points to a GeoDataFrame
gdf_points = gpd.GeoDataFrame(geometry=all_points, crs="EPSG:32632")

# Transform back to WGS84 (lat/lon)
gdf_points = gdf_points.to_crs(epsg=4326)

# Extract coordinates
coords = [(point.y, point.x) for point in gdf_points.geometry]

print(f"Generated {len(coords)} points")  # Debugging

# Save as CSV
pd.DataFrame(coords, columns=["latitude", "longitude"]).to_csv("bologna_streetview_coords.csv", index=False)

# Plot in Folium
if coords:
    avg_lat = sum(lat for lat, lon in coords) / len(coords)
    avg_lon = sum(lon for lat, lon in coords) / len(coords)
    map_center = [avg_lat, avg_lon]
else:
    map_center = [44.4949, 11.3426]  # Fallback

m = folium.Map(location=map_center, zoom_start=13)
for lat, lon in coords:
    folium.CircleMarker([lat, lon], radius=5, color="blue", fill=True).add_to(m)

m.save("bologna_map.html")
webbrowser.open("bologna_map.html")
