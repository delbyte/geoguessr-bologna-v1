import torch
import torchvision.transforms as transforms
from PIL import Image
import argparse
from architectures.resnet import ResNetGeolocation
from architectures.mobilenet import MobileNetGeolocation
import os

# Import the reverse geocoding utility from your external utils folder
from utils.reverse_geocode import reverse_geocode

# Set up argument parser for command-line input
parser = argparse.ArgumentParser(description="Inference for GeoGuessr Model")
parser.add_argument("--image", type=str, required=True, help="Path to the input image")
parser.add_argument("--model_type", type=str, default="resnet", choices=["resnet", "mobilenet"], help="Type of model to use")
parser.add_argument("--checkpoint", type=str, required=True, help="Path to model checkpoint")
args = parser.parse_args()

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define transforms: For inference, we typically do not apply random augmentations.
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load and preprocess the image
img = Image.open(args.image).convert("RGB")
img = transform(img).unsqueeze(0).to(DEVICE)

# Initialize Model based on chosen type
if args.model_type == "resnet":
    model = ResNetGeolocation().to(DEVICE)
elif args.model_type == "mobilenet":
    model = MobileNetGeolocation().to(DEVICE)
else:
    raise ValueError("Invalid model type.")

# Load the checkpoint
model.load_state_dict(torch.load(args.checkpoint, map_location=DEVICE))
model.eval()

# Inference
with torch.no_grad():
    output = model(img)

# Assume outputs are in the same normalized scale as training targets.
predicted_lat, predicted_lon = output[0].cpu().numpy()
print(f"Predicted Coordinates (normalized): {predicted_lat:.4f}, {predicted_lon:.4f}")

# Reverse geocode the prediction to a human-readable address
address = reverse_geocode(predicted_lat, predicted_lon)
print("Reverse Geocoded Address:", address)
