import requests
import json
import osmnx as ox
import folium
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import unary_union
import geojson
import webbrowser

# Mapillary Client ID
CLIENT_ID = "10021959651168330"

# OAuth URL for user authorization
AUTH_URL = f"https://www.mapillary.com/connect?client_id=10021959651168330"

# Step 1: Get Authorization
print(f"Open this URL in your browser and log in to authorize:\n{AUTH_URL}")
webbrowser.open(AUTH_URL)  
access_token = input("Paste the access token from the redirected URL: ")

# Step 2: Define API Endpoint & Headers
MAPILLARY_IMAGES_ENDPOINT = "https://graph.mapillary.com/images"
headers = {"Authorization": f"Bearer {access_token}"}
# Step 3: Get Bologna's Road Network & Compute Convex Hull
city = "Bologna, Italy"
G = ox.graph_from_place(city, network_type="drive")

edges = ox.graph_to_gdfs(G, nodes=False)
road_geometries = edges.geometry.tolist()
convex_hull = unary_union(road_geometries).convex_hull

convex_hull_geojson = geojson.Feature(geometry=convex_hull.__geo_interface__, properties={})

# Step 4: Fetch Mapillary Images Within Bologna's Convex Hull
def fetch_mapillary_images(geometry):
    """Fetch all images from Mapillary within the provided geometry using pagination."""
    params = {
        "access_token": access_token,  # Correct way to authenticate
        "fields": "id,geometry",
        "limit": 100
    }
    url = MAPILLARY_IMAGES_ENDPOINT
    images = []

    while url:
        response = requests.post(url, json={"geometry": geometry}, params=params)
        response.raise_for_status()
        data = response.json()
        images.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")  # Pagination

    return images


images = fetch_mapillary_images(convex_hull_geojson["geometry"])

# Step 5: Estimate Disk Space Needed
ESTIMATED_SIZE_MB_PER_IMAGE = 0.5
total_images = len(images)
total_estimated_size_mb = total_images * ESTIMATED_SIZE_MB_PER_IMAGE

print(f"Total images: {total_images}")
print(f"Estimated disk space needed: {total_estimated_size_mb:.2f} MB")

# Step 6: Save Image Coordinates
image_coords = [{"id": img["id"], "coordinates": img["geometry"]["coordinates"]} for img in images]
with open("bologna_image_coordinates.json", "w") as f:
    json.dump(image_coords, f, indent=4)

# Step 7: Create & Display a Folium Map
map_center = [convex_hull.centroid.y, convex_hull.centroid.x]
m = folium.Map(location=map_center, zoom_start=13)

for img in image_coords:
    lat, lon = img["coordinates"][1], img["coordinates"][0]
    folium.CircleMarker([lat, lon], radius=5, color="blue", fill=True).add_to(m)

m.save("bologna_map.html")
print("Map saved as bologna_map.html")
