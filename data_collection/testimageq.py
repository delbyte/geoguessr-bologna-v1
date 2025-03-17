import requests
import json
import folium
import webbrowser

# Replace with your Mapillary Client ID
CLIENT_ID = "10021959651168330"

# Redirect user to authorize
auth_url = f"https://www.mapillary.com/connect?client_id={CLIENT_ID}&response_type=token&scope=user:read"
print("Opening browser for authentication...")
webbrowser.open(auth_url)

MAPILLARY_ACCESS_TOKEN = input("Enter your Mapillary access token: ")

print("After authorizing, copy the access token from the URL and paste it in the script.")

# Define the bounding box (Bologna)
bbox = "11.2296206,44.4210532,11.4336079,44.556094"

# API request URL
url = f"https://graph.mapillary.com/images?access_token={MAPILLARY_ACCESS_TOKEN}&bbox={bbox}&fields=id,geometry"

print("Fetching image locations from Mapillary...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Data received successfully.")

    # Extract coordinates
    image_coords = [(img["geometry"]["coordinates"][1], img["geometry"]["coordinates"][0]) for img in data["data"]]

    print(f"Total images found: {len(image_coords)}")

    # Create a Folium map
    print("Creating Folium map...")
    bologna_map = folium.Map(location=[44.4939, 11.3426], zoom_start=12)

    # Add markers for each image
    print("Adding markers to the map...")
    for lat, lon in image_coords:
        folium.Marker(location=[lat, lon], popup=f"Image at ({lat}, {lon})").add_to(bologna_map)

    # Save the map
    print("Saving map as 'bologna_map.html'...")
    bologna_map.save("bologna_map.html")

    webbrowser.open("bologna_map.html")
else:
    print("Error fetching Mapillary data:", response.text)


    #rest day
