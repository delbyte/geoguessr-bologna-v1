import osmnx as ox
import folium
import json
import subprocess
import geopandas as gpd
from shapely.geometry import Point

# Step 1: Get the bounding box of Bologna using OSMnx
print("Fetching bounding box for Bologna, Italy...")
place_name = "Bologna, Italy"
graph = ox.graph_from_place(place_name, network_type="all")
gdf = ox.geocode_to_gdf(place_name)
minx, miny, maxx, maxy = gdf.total_bounds  # Get bounding box
print(f"Bounding box: MinX={minx}, MinY={miny}, MaxX={maxx}, MaxY={maxy}")

# Step 2: Use mapillary_tools to fetch image metadata
output_file = "mapillary_images.geojson"
command = f"mapillary_tools search --bbox {miny},{minx},{maxy},{maxx} --geojson --output {output_file}"
print(f"Running Mapillary command:\n{command}")

try:
    subprocess.run(command, shell=True, check=True)
    print("Mapillary data successfully retrieved and saved.")
except subprocess.CalledProcessError as e:
    print(f"Error fetching Mapillary data: {e}")
    exit(1)

# Step 3: Parse the GeoJSON file to extract image coordinates
print(f"Reading GeoJSON file: {output_file}...")
try:
    with open(output_file, "r") as f:
        data = json.load(f)
    print("GeoJSON file successfully loaded.")
except FileNotFoundError:
    print(f"Error: {output_file} not found.")
    exit(1)

image_coords = []
print("Extracting image coordinates...")
for feature in data["features"]:
    lon, lat = feature["geometry"]["coordinates"]
    image_coords.append((lat, lon))
print(f"Extracted {len(image_coords)} image coordinates.")

# Step 4: Display images on a folium map
print("Creating Folium map...")
bologna_map = folium.Map(location=[(miny + maxy) / 2, (minx + maxx) / 2], zoom_start=13)

print("Adding markers to the map...")
for lat, lon in image_coords:
    folium.Marker(location=[lat, lon], popup=f"Image at ({lat}, {lon})").add_to(bologna_map)

# Step 5: Print total image count and save the map
print(f"Total images found: {len(image_coords)}")
bologna_map.save("bologna_map.html")
print("Map successfully saved as bologna_map.html. Open it in a browser to view.")

