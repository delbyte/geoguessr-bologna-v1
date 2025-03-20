import json
import csv

json_file = "dataset/unnamed"
csv_file = "dataset/finaldata.csv"
image_folder = "dataset/images_resized"

# load JSON data
with open(json_file, "r") as f:
    data = json.load(f)

# write data in csv
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["image_id", "latitude", "longitude"])  # CSV header

    for image_id, coords in data.items():
        image_path = f"{image_folder}/{image_id}.jpg"
        writer.writerow([image_path, coords[0], coords[1]]) 

print(f"CSV saved at {csv_file}")
