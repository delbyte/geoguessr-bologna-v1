import torch
import torchvision.transforms as transforms
from PIL import Image
import argparse
from model.architectures.resnet import ResNetGeolocation
from model.architectures.mobilenet import MobileNetGeolocation
import os
from utils.reverse_geocode import reverse_geocode
import webbrowser
from utils.visualise import plot_locations

# Set up argument parser
parser = argparse.ArgumentParser(description="Inference for GeoGuessr Model")
parser.add_argument("--image", type=str, required=True, help="Path to the input image")
parser.add_argument("--actual_coords", type=float, nargs=2, required=True, help="Actual latitude and longitude of the image")
parser.add_argument("--model_type", type=str, default="resnet", choices=["resnet", "mobilenet"], help="Type of model to use")
parser.add_argument("--checkpoint", type=str, required=True, help="Path to model checkpoint")
args = parser.parse_args()

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Dataset min/max latitudes and longitudes
lat_min, lat_max = 44.4210532, 44.556094
lon_min, lon_max = 11.2296206, 11.4336079

# Function to denormalize predictions
def denormalize(normalized_lat, normalized_lon, lat_min, lat_max, lon_min, lon_max):
    lat = normalized_lat * (lat_max - lat_min) + lat_min
    lon = normalized_lon * (lon_max - lon_min) + lon_min
    return lat, lon

# Define image transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load and preprocess the image
img = Image.open(args.image).convert("RGB")
img = transform(img).unsqueeze(0).to(DEVICE)

# Initialize model
if args.model_type == "resnet":
    model = ResNetGeolocation().to(DEVICE)
elif args.model_type == "mobilenet":
    model = MobileNetGeolocation().to(DEVICE)
else:
    raise ValueError("Invalid model type.")

# Load model checkpoint
model.load_state_dict(torch.load(args.checkpoint, map_location=DEVICE))
model.eval()

# Inference
with torch.no_grad():
    output = model(img)

# Extract predicted coordinates and de-normalize
normalized_lat, normalized_lon = output[0].cpu().numpy()
predicted_lat, predicted_lon = denormalize(normalized_lat, normalized_lon, lat_min, lat_max, lon_min, lon_max)

print(f"Predicted Coordinates: {predicted_lat:.4f}, {predicted_lon:.4f}")

# Reverse geocode the predicted location
address = reverse_geocode(predicted_lat, predicted_lon)
print("Reverse Geocoded Address:", address)

# Plot actual and predicted locations on a map
map_filename = plot_locations(actual_coords=(args.actual_coords[0], args.actual_coords[1]),
                              predicted_coords=(predicted_lat, predicted_lon))
print(f"Map saved as: {map_filename}")
webbrowser.open(map_filename)
