from flask import Flask, request, jsonify
import os
import uuid
import base64
from flask_cors import CORS
from detect import detect_and_crop_by_keyword
from object_detection.depth import generate_depth_map
from object_detection.merge_ply import merge_ply_files
from object_detection.mesh import generate_mesh

app = Flask(__name__)
CORS(app)

INPUT_FOLDER = "extension_data"
PLY_FOLDER = 'output_ply'
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
        # TODO : Check the best image out of all

    return jsonify({"status": "success", "matched_crops": all_crops})

@app.route("/background", methods=["POST"])
def background():
    data = request.get_json()
    backGroundImage = data.get("Image")

    if not backGroundImage:
        return jsonify({"status": "error", "message": "Missing 'Image'"}), 400

    unique_name = "Background.jpg"
    image_path = os.path.join(INPUT_FOLDER, unique_name)
    
    try:
        with open(image_path, "wb") as f:
            f.write(image_data) 
        return jsonify({"status": "success", "message": "Image saved successfully"})
    except Exception as e:
        print(f"Failed to save image: {e}")
        return jsonify({"status": "error", "message": f"Failed to save image: {str(e)}"}), 500
    

@app.route("/depthMap", methods=["GET"])
def depthMap():
    backGroundImage = os.path.join(INPUT_FOLDER, 'Background.jpg')
    objectImage = os.path.join(INPUT_FOLDER, 'Object.jpg')
    DEPTHMAP_FOLDER = "./depth_maps"
    generate_depth_map(backGroundImage, DEPTHMAP_FOLDER, 'Background.jpg')
    generate_depth_map(objectImage, DEPTHMAP_FOLDER, 'Object.jpg')
    generate_mesh(backGroundImage, os.path.join(DEPTHMAP_FOLDER, 'Background.jpg'), os.join.path(PLY_FOLDER))
    generate_mesh(backGroundImage, os.path.join(DEPTHMAP_FOLDER), 'Object.jpg', os.join.path(PLY_FOLDER))
    merge_ply_files(os.path.join(PLY_FOLDER, 'Background.ply'), os.path.join(PLY_FOLDER, 'Object.ply'), os.path.join(PLY_FOLDER, 'Merged.ply'))
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
