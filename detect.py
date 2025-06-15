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

def detect_and_crop_highest_confidence(image_path, keyword=None, output_folder="output_crops", conf_threshold=0.5):
    """Detect objects in image and save the crop with the highest confidence if it matches the keyword."""
    os.makedirs(output_folder, exist_ok=True)
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"⚠️ Failed to load image: {image_path}")
        return None

    results = model(image)[0]  # First result set
    image_name = os.path.basename(image_path)
    highest_conf_crop = None
    max_conf = conf_threshold  # Start with the threshold to ensure only valid crops are considered

    for i, box in enumerate(results.boxes):
        conf = float(box.conf)
        if conf < conf_threshold:
            continue  # Skip low-confidence detections

        cls_id = int(box.cls)
        cls_name = class_names[cls_id]

        if keyword and keyword.lower() != cls_name.lower():
            continue  # Skip if keyword is given and doesn't match

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cropped = image[y1:y2, x1:x2]

        # Keep track of highest confidence crop
        if conf > max_conf:
            max_conf = conf
            highest_conf_crop = {
                "class": cls_name,
                "confidence": round(conf, 2),
                "crop_path": os.path.join(output_folder, f"{os.path.splitext(image_name)[0]}_{cls_name}.jpg")
            }

    # Save the highest-confidence crop if one was found
    if highest_conf_crop:
        cv2.imwrite(highest_conf_crop["crop_path"], cropped)
        return highest_conf_crop, 
    
    return None
