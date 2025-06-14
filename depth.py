import os
import cv2
import numpy as np
import onnxruntime as ort


MODEL_PATH = "./midas-midas-v2-float.onnx"


# # Folder containing images
# INPUT_FOLDER = "./extension_data"
# OUTPUT_FOLDER = "./depth_maps"


session = ort.InferenceSession(MODEL_PATH)

def process_image(image_path):
    """Load an image and generate a depth map using the ONNX model."""
    image = cv2.imread(image_path)
    image = cv2.resize(image, (256, 256)) 
    # image = cv2.resize(image, (518, 518))  # Resize to model's expected input size
    image = image.astype(np.float32) / 255.0  
    image = np.transpose(image, (2, 0, 1)) 
    image = np.expand_dims(image, axis=0)  

  
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    depth_map = session.run([output_name], {input_name: image})[0]


    depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min()) * 255.0
    depth_map = depth_map.astype(np.uint8)
    depth_map = np.squeeze(depth_map)

    return depth_map

def generate_depth_map(image_path, output_folder, filename):
    """Process all images in a given folder."""
    os.makedirs(output_folder, exist_ok=True)
    
    depth_map = process_image(image_path)
    
    output_path = os.path.join(output_folder, f"{filename}")
    print(f"Depth Map Shape: {depth_map.shape}, Data Type: {depth_map.dtype}")

    cv2.imwrite(output_path, depth_map, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"Saved depth map: {output_path}")


# process_folder(INPUT_FOLDER, OUTPUT_FOLDER)
