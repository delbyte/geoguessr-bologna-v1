import numpy as np
from shapely.geometry import LineString, Point
import osmnx as ox
import geopandas as gpd
import pandas as pd
import folium
import webbrowser
import requests
import json

# Your Mapillary access token
ACCESS_TOKEN = 'YOUR_MAPILLARY_ACCESS_TOKEN'

# Mapillary Images API endpoint
MAPILLARY_IMAGES_ENDPOINT = 'https://graph.mapillary.com/images'

# Define the Area of Interest (AOI) as a GeoJSON object
# Replace this with your actual GeoJSON geometry for Bologna's road network
aoi_geojson = {
    "type": "Polygon",
    "coordinates": [
        [
            [11.295, 44.490],
            [11.295, 44.510],
            [11.335, 44.510],
            [11.335, 44.490],
            [11.295, 44.490]
        ]
    ]
}

# Function to fetch image metadata within the AOI
def fetch_mapillary_images(aoi_geojson, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'fields': 'id,geometry',
        'limit': 100  # Maximum allowed by the API
    }
    images = []
    url = MAPILLARY_IMAGES_ENDPOINT

    while url:
        response = requests.post(
            url,
            json={'geometry': aoi_geojson},
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        images.extend(data.get('data', []))
        # Check for pagination
        url = data.get('paging', {}).get('next', None)

    return images

# Fetch images
images = fetch_mapillary_images(aoi_geojson, ACCESS_TOKEN)

# Calculate estimated size per image (in megabytes)
# This is an approximation; actual sizes may vary
ESTIMATED_SIZE_MB_PER_IMAGE = 0.5

# Calculate total estimated disk space required
total_images = len(images)
total_estimated_size_mb = total_images * ESTIMATED_SIZE_MB_PER_IMAGE

# Output results
print(f'Total number of images: {total_images}')
print(f'Total estimated disk space required: {total_estimated_size_mb:.2f} MB')

# Optional: Save image coordinates to a JSON file
image_coords = [{'id': img['id'], 'coordinates': img['geometry']['coordinates']} for img in images]
with open('bologna_image_coordinates.json', 'w') as f:
    json.dump(image_coords, f, indent=4)

