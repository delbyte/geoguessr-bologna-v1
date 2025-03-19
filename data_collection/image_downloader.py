#Partial Credits: https://gist.github.com/cbeddow/79d68aa6ed0f028d8dbfdad2a4142cf5

import mercantile, mapbox_vector_tile, requests, json, os
from vt2geojson.tools import vt_bytes_to_geojson
    
# define an empty geojson as output
output= { "type": "FeatureCollection", "features": [] }

# vector tile endpoints -- change this in the API request to reference the correct endpoint
tile_coverage = 'mly1_public'

# tile layer depends which vector tile endpoints: 
# 1. if map features or traffic signs, it will be "point" always
# 2. if looking for coverage, it will be "image" for points, "sequence" for lines, or "overview" for far zoom
tile_layer = "image"

# Mapillary access token -- user should provide their own
access_token = 'MLY|10021959651168330|f0e52ee7758ab85150bce8631f498ee8'

# a bounding box in [east_lng,_south_lat,west_lng,north_lat] format
west, south, east, north = [11.2296206, 44.4210532, 11.4336079, 44.556094] #bologna bbox

# get the list of tiles with x and y coordinates which intersect our bounding box
# MUST be at zoom level 14 where the data is available, other zooms currently not supported
tiles = list(mercantile.tiles(west, south, east, north, 14))

# Define a dictionary to store image ID and coordinates
image_coordinates = {}

# Ensure the images directory exists
images_dir = os.path.join('..', 'dataset', 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# loop through list of tiles to get tile z/x/y to plug in to Mapillary endpoints and make request
for tile in tiles:
    tile_url = 'https://tiles.mapillary.com/maps/vtp/{}/2/{}/{}/{}?access_token={}'.format(tile_coverage,tile.z,tile.x,tile.y,access_token)
    response = requests.get(tile_url)
    data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer=tile_layer)

    # push to output geojson object if yes
    for feature in data['features']:
        # get lng,lat of each feature
        lng = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]

        # ensure feature falls inside bounding box since tiles can extend beyond
        if lng > west and lng < east and lat > south and lat < north:
            # request the URL of each image
            image_id = feature['properties']['id']
            header = {'Authorization': 'OAuth {}'.format(access_token)}
            url = 'https://graph.mapillary.com/{}?fields=thumb_2048_url'.format(image_id)
            r = requests.get(url, headers=header)
            data = r.json()
            image_url = data['thumb_2048_url']

            # save each image with ID as filename to the images directory
            image_path = os.path.join(images_dir, '{}.jpg'.format(image_id))
            with open(image_path, 'wb') as handler:
                image_data = requests.get(image_url, stream=True).content
                handler.write(image_data)

            # Store the image ID and coordinates in the dictionary
            image_coordinates[image_id] = (lng, lat)

# Save the dictionary to a JSON file
with open(os.path.join('..', 'dataset', 'unnamed.json'), 'w') as f:
    json.dump(image_coordinates, f)

# Print the dictionary of image coordinates
print(image_coordinates)
