import cv2
import os
from tqdm import tqdm

input_folder = "dataset/images"
output_folder = "dataset/images_resized"
target_size = (224, 224)  # can use 256,256

os.makedirs(output_folder, exist_ok=True)

for img_name in tqdm(os.listdir(input_folder)):
    img_path = os.path.join(input_folder, img_name)
    img = cv2.imread(img_path)
    if img is None:
        continue
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(output_folder, img_name), img)
