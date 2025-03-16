import requests
import osmnx as ox
import folium
from shapely.ops import unary_union
from shapely.geometry import Point
import time
import json
import webbrowser
"""
# ===============================
# Step 0: OAuth Authentication
# ===============================
# Replace with your Mapillary Client ID
CLIENT_ID = "10021959651168330"
AUTH_URL = f"https://www.mapillary.com/connect?client_id={CLIENT_ID}&response_type=token"

print("Please open the following URL in your browser to authenticate with Mapillary:")
print(AUTH_URL)
webbrowser.open(AUTH_URL)

access_token = input("After authenticating, please paste the access token here: ")
"""
# ========================================
# Step 1: Compute Convex Hull of Bologna's Road Network
# ========================================
city = "Bologna, Italy"
G = ox.graph_from_place(city, network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False)

# Combine all road geometries and compute the convex hull
convex_hull = unary_union(edges.geometry.tolist()).convex_hull

# Derive the bounding box from the convex hull (format: west,south,east,north)
minx, miny, maxx, maxy = convex_hull.bounds
mybbox = ([minx, miny, maxx, maxy])
print(f"Computed bounding box: {mybbox}")

B = ox.graph_from_bbox(mybbox, network_type="all")
ox.plot_graph(B)
"""
# ========================================
# Step 2: Fetch Mapillary Images Within the Bounding Box Using Pagination
# ========================================
MAPILLARY_IMAGES_ENDPOINT = "https://graph.mapillary.com/images"

def fetch_mapillary_images(bbox, access_token):
    params = {
        "access_token": access_token,
        "fields": "id,geometry",
        "limit": 100,  # Maximum allowed per request
        "bbox": bbox
    }
    images = []
    url = MAPILLARY_IMAGES_ENDPOINT

    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        images.extend(data.get("data", []))
        # Use the pagination URL from the response, if available
        url = data.get("paging", {}).get("next")
        # Clear params for subsequent requests since they're now in the URL
        params = {}
        # Pause briefly to avoid rate limiting
        time.sleep(0.2)
    return images

images = fetch_mapillary_images(bbox, access_token)

# ========================================
# Step 3: Filter Images to Only Those Within the Convex Hull
# ========================================
def is_within_convex_hull(image, convex_hull):
    # Mapillary returns coordinates as [longitude, latitude]
    lon, lat = image["geometry"]["coordinates"]
    point = Point(lon, lat)
    return convex_hull.contains(point)

filtered_images = [img for img in images if is_within_convex_hull(img, convex_hull)]

# ========================================
# Step 4: Estimate Storage Requirements and Save Coordinates
# ========================================
ESTIMATED_SIZE_MB_PER_IMAGE = 0.5  # Estimated average size per image in MB
total_images = len(filtered_images)
total_estimated_size_mb = total_images * ESTIMATED_SIZE_MB_PER_IMAGE

print(f"Total number of images within convex hull: {total_images}")
print(f"Estimated disk space needed: {total_estimated_size_mb:.2f} MB")

# Save image coordinates and IDs to a JSON file
image_coords = [{"id": img["id"], "coordinates": img["geometry"]["coordinates"]} for img in filtered_images]
with open("bologna_image_coordinates.json", "w") as f:
    json.dump(image_coords, f, indent=4)

# ========================================
# Step 5: Map the Image Locations Using Folium
# ========================================
map_center = [convex_hull.centroid.y, convex_hull.centroid.x]
m = folium.Map(location=map_center, zoom_start=13)

for img in image_coords:
    # Unpack coordinates: Mapillary returns [longitude, latitude]
    lon, lat = img["coordinates"]
    folium.CircleMarker([lat, lon], radius=5, color="blue", fill=True).add_to(m)

m.save("bologna_map.html")
print("Map saved as 'bologna_map.html'")
webbrowser.open("bologna_map.html")
"""