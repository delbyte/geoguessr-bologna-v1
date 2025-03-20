import mercantile, mapbox_vector_tile, requests, json, os
from vt2geojson.tools import vt_bytes_to_geojson

# Define an empty GeoJSON output
output = {"type": "FeatureCollection", "features": []}

tile_coverage = 'mly1_public'
tile_layer = "image"

access_token = 'MLY|10021959651168330|f0e52ee7758ab85150bce8631f498ee8'

west, south, east, north = [11.2296206, 44.4210532, 11.4336079, 44.556094]  # Bologna BBox

tiles = list(mercantile.tiles(west, south, east, north, 14))

image_coordinates = {}
images_dir = os.path.join('..', 'dataset', 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

json_path = os.path.join('..', 'dataset', 'unnamed.json')

# load existing JSON data if available (to resume progress)
if os.path.exists(json_path):
    try:
        with open(json_path, 'r') as f:
            image_coordinates = json.load(f)
    except json.JSONDecodeError:
        image_coordinates = {}

image_count = 0  # Counter for batch saving

for tile in tiles:
    try:
        tile_url = f'https://tiles.mapillary.com/maps/vtp/{tile_coverage}/2/{tile.z}/{tile.x}/{tile.y}?access_token={access_token}'
        response = requests.get(tile_url)
        data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer=tile_layer)
    
        for feature in data['features']:
            try:
                lng, lat = feature['geometry']['coordinates']
                if not (west < lng < east and south < lat < north):
                    continue  # skip features outside bounding box
                
                image_id = feature['properties']['id']
                if image_id in image_coordinates:
                    continue
                
                header = {'Authorization': f'OAuth {access_token}'}
                url = f'https://graph.mapillary.com/{image_id}?fields=thumb_2048_url'
                r = requests.get(url, headers=header)
                data = r.json()
                image_url = data.get('thumb_2048_url')
                if not image_url:
                    continue  # url missing exception
                
                image_path = os.path.join(images_dir, f'{image_id}.jpg')
                with open(image_path, 'wb') as handler:
                    handler.write(requests.get(image_url, stream=True).content)
                
                image_coordinates[image_id] = (lng, lat)
                image_count += 1

                if image_count % 10 == 0:  # save every 10 images
                    with open(json_path, 'w') as f:
                        json.dump(image_coordinates, f, indent=4)
                    print(f"Saved progress at {image_count} images.")
            
            except Exception as e:
                print(f"Error processing image {image_id}: {e}")
    
    except Exception as e:
        print(f"Error processing tile {tile.x}, {tile.y}: {e}")

# Final save at the end
with open(json_path, 'w') as f:
    json.dump(image_coordinates, f, indent=4)
print("All images processed and saved successfully.")
