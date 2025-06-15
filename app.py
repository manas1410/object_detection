from flask import Flask, request, jsonify
import os
import uuid
import base64
from flask_cors import CORS
from detect import detect_and_crop_by_keyword

app = Flask(__name__)
CORS(app)

INPUT_FOLDER = "extension_data"
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
    keyword = data.get("keyword")
    image_blobs = data.get("imageBlobs")
    
    print(data)
    print(keyword)
    
    if not keyword or not image_blobs:
        return jsonify({"status": "error", "message": "Missing 'keyword' or 'images'"}), 400

    all_crops = []
    
    for blob_data in image_blobs:
        print("Processing blob image...")
        unique_name = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(INPUT_FOLDER, unique_name)

        try:
            # Convert blob data (buffer object) to bytes
            if isinstance(blob_data, dict) and 'data' in blob_data:
                # Buffer object format: {"type": "Buffer", "data": [255, 216, 255, ...]}
                image_bytes = bytes(blob_data['data'])
            elif isinstance(blob_data, list):
                # Direct array format: [255, 216, 255, ...]
                image_bytes = bytes(blob_data)
            else:
                print(f"Unexpected blob data format: {type(blob_data)}")
                continue  # Skip this image
            
            # Save the image
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            print(f"Successfully saved blob image to {image_path}")
            
            # Process the image
            crops = detect_and_crop_by_keyword(image_path, keyword)
            all_crops.extend(crops)
            
        except Exception as e:
            print(f"Failed to process blob image: {e}")
            continue  # Skip this image and continue with others

    return jsonify({"status": "success", "matched_crops": all_crops})

@app.route("/background", methods=["POST"])
def background():
    data = request.get_json()
    image_buffer_data = data.get("imageUrl")

    if not image_buffer_data:
        return jsonify({"status": "error", "message": "Missing 'Image'"}), 400

    unique_name = "BackGround.jpg"
    image_path = os.path.join(INPUT_FOLDER, unique_name)
    
    try:
        if isinstance(image_buffer_data, dict) and 'data' in image_buffer_data:
            # Buffer object format: {"type": "Buffer", "data": [255, 216, 255, ...]}
            image_bytes = bytes(image_buffer_data['data'])
        elif isinstance(image_buffer_data, list):
            # Direct array format: [255, 216, 255, ...]
            image_bytes = bytes(image_buffer_data)
        else:
            raise ValueError("Unexpected image data format")

        with open(image_path, "wb") as f:
            f.write(image_bytes) 
        return jsonify({"status": "success", "message": "Image saved successfully"})
    except Exception as e:
        print(f"Failed to save image: {e}")
        return jsonify({"status": "error", "message": f"Failed to save image: {str(e)}"}), 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)
