import osmnx as ox
import folium
import json
import subprocess
import geopandas as gpd
from shapely.geometry import Point

# Step 1: Get the bounding box of Bologna using OSMnx
place_name = "Bologna, Italy"
graph = ox.graph_from_place(place_name, network_type="all")
gdf = ox.geocode_to_gdf(place_name)
minx, miny, maxx, maxy = gdf.total_bounds  # Get bounding box

# Step 2: Use mapillary_tools to fetch image metadata
output_file = "mapillary_images.geojson"
command = f"mapillary_tools search --bbox {miny},{minx},{maxy},{maxx} --geojson --output {output_file}"
subprocess.run(command, shell=True, check=True)

# Step 3: Parse the GeoJSON file to extract image coordinates
with open(output_file, "r") as f:
    data = json.load(f)

image_coords = []
for feature in data["features"]:
    lon, lat = feature["geometry"]["coordinates"]
    image_coords.append((lat, lon))

# Step 4: Display images on a folium map
bologna_map = folium.Map(location=[(miny + maxy) / 2, (minx + maxx) / 2], zoom_start=13)

for lat, lon in image_coords:
    folium.Marker(location=[lat, lon], popup=f"Image at ({lat}, {lon})").add_to(bologna_map)

# Step 5: Print total image count and save the map
print(f"Total images found: {len(image_coords)}")
bologna_map.save("bologna_map.html")
print("Map saved as bologna_map.html")
