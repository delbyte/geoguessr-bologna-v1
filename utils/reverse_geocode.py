import requests

def reverse_geocode(lat: float, lon: float) -> str:
    """
    Given latitude and longitude, returns a human-readable address
    using Nominatim's reverse geocoding API.
    """

    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "jsonv2",
        "zoom": 18           # maximum zoom level for detailed address
    }
    headers = {
        "User-Agent": "GeoGuessr-Bologna-V1/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        address = data.get("display_name", "Unknown location")
        return address
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return "Unknown location"
