import os
import cv2
import requests
from ultralytics import YOLO

# Load model
model = YOLO("yolov8n.pt")
class_names = model.names

def download_image(url, save_path):
    """Download image from a URL and save locally."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return False

def detect_and_crop_by_keyword(image_path, keyword=None, output_folder="output_crops", conf_threshold=0.5):
    """Detect objects in image and save crops that match keyword (if given) with >conf_threshold confidence."""
    os.makedirs(output_folder, exist_ok=True)
    image = cv2.imread(image_path)
    if image is None:
        print(f"⚠️ Failed to load image: {image_path}")
        return []

    results = model(image)[0]  # First result set
    image_name = os.path.basename(image_path)
    matched_crops = []

    for i, box in enumerate(results.boxes):
        conf = float(box.conf)
        if conf < conf_threshold:
            continue  # skip low-confidence boxes

        cls_id = int(box.cls)
        cls_name = class_names[cls_id]

        if keyword and keyword.lower() != cls_name.lower():
            continue  # skip if keyword given and doesn't match

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cropped = image[y1:y2, x1:x2]

        crop_filename = f"{os.path.splitext(image_name)[0]}_{cls_name}_{i}.jpg"
        crop_path = os.path.join(output_folder, crop_filename)
        cv2.imwrite(crop_path, cropped)

        matched_crops.append({
            "class": cls_name,
            "confidence": round(conf, 2),
            "crop_path": crop_path
        })

    return matched_crops
