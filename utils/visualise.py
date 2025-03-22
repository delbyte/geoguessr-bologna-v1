import folium

def plot_locations(actual_coords, predicted_coords):
    """
    Plots actual and predicted locations on a map.
    :param actual_coords: Tuple of (lat, lon) for the actual image location.
    :param predicted_coords: Tuple of (lat, lon) for the AI-predicted location.
    """
    # Center the map around the actual coordinates
    m = folium.Map(location=actual_coords, zoom_start=14)
    
    # Add actual location marker
    folium.Marker(
        location=actual_coords,
        popup="Actual Location",
        icon=folium.Icon(color="green", icon="info-sign")
    ).add_to(m)
    
    # Add predicted location marker
    folium.Marker(
        location=predicted_coords,
        popup="Predicted Location",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    
    # Draw a line between actual and predicted locations
    folium.PolyLine([actual_coords, predicted_coords], color='blue', weight=2.5, opacity=0.8).add_to(m)
    
    # Save and display the map
    map_filename = "location_comparison_map.html"
    m.save(map_filename)
    print(f"Map saved as {map_filename}")
    
    return map_filename  # You can open this file in a browser
