from flask import Flask, request, jsonify
import os
import uuid
import base64
from flask_cors import CORS
from detect import detect_and_crop_by_keyword

app = Flask(__name__)
CORS(app)

INPUT_FOLDER = "input_data"
os.makedirs(INPUT_FOLDER, exist_ok=True)

def save_base64_image(base64_str, output_path):
    try:
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(base64_str.split(',')[-1]))  # handles data:image/...;base64,
        return True
    except Exception as e:
        print(f"Failed to decode base64 image: {e}")
        return False

@app.route("/detect", methods=["POST"])
def detect():
    data = request.get_json()
    keyword = data.get("Keyword")
    base64_images = data.get("Images")

    if not keyword or not base64_images:
        return jsonify({"status": "error", "message": "Missing 'keyword' or 'images'"}), 400

    all_crops = []
    for base64_img in base64_images:
        unique_name = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(INPUT_FOLDER, unique_name)

        if not save_base64_image(base64_img, image_path):
            continue  # skip failures

        crops = detect_and_crop_by_keyword(image_path, keyword)
        all_crops.extend(crops)

    return jsonify({"status": "success", "matched_crops": all_crops})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
