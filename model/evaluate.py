import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from architectures.resnet import ResNetGeolocation
from architectures.mobilenet import MobileNetGeolocation
from model.utils.dataloader import GeolocationDataset, transform
import os

# Configurations
CSV_PATH = ""  # TODO- make a valid path
BATCH_SIZE = 16
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_TYPE = "resnet"  # or "mobilenet"
CHECKPOINT_PATH = "model/checkpoints/resnet_epoch20.pth"  # Update as needed

# Load Dataset (validation set)
dataset = GeolocationDataset(csv_file=CSV_PATH, transform=transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

# Initialize Model
if MODEL_TYPE == "resnet":
    model = ResNetGeolocation().to(DEVICE)
elif MODEL_TYPE == "mobilenet":
    model = MobileNetGeolocation().to(DEVICE)
else:
    raise ValueError("Invalid MODEL_TYPE. Choose 'resnet' or 'mobilenet'.")

# Load Checkpoint
model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=DEVICE))
model.eval()

criterion = nn.MSELoss()

# Evaluation Loop
total_loss = 0.0
with torch.no_grad():
    for images, targets in dataloader:
        images, targets = images.to(DEVICE), targets.to(DEVICE)
        outputs = model(images)
        loss = criterion(outputs, targets)
        total_loss += loss.item()

avg_loss = total_loss / len(dataloader)
print(f"Validation MSE Loss: {avg_loss:.4f}")
