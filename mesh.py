import numpy as np
import cv2

import vtk
import os

INPUT_RGB = "./extension_data"
INPUT_DEPTH_MAP = "./depth_maps"
OUTPUT_FOLDER = "./output_ply"

def generate_vtk_point_cloud(image_path, depth_path, output_ply, sample_ratio=0.01):
    """Generates a 3D point cloud with correctly scaled depth and RGB colors."""
    
    # Load images
    rgb_image = cv2.imread(image_path)
    depth_map = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)

    # Resize depth map to match RGB image dimensions
    depth_map = cv2.resize(depth_map, (rgb_image.shape[1], rgb_image.shape[0]), interpolation=cv2.INTER_NEAREST)

    height, width = depth_map.shape
    points = []
    colors = []

    focal_length = 750  # Adjusted for better perspective correction
    depth_scale_factor = 0.002  # Scaling factor to fit real-world depth

    rotation_matrix = np.array([
        [1,  0,  0],  
        [0, -1,  0],  
        [0,  0, -1] 
    ])

    for y in range(height):
        for x in range(width):
            # Normalize depth & prevent extreme scaling
            z = (depth_map[y, x] / 255.0) * depth_scale_factor  
            # z = (depth_map[y, x] / 255.0) * depth_scale_factor  * -1
            if z > 0:  # Ignore zero-depth points
                X = (x - width // 2) * z / focal_length  
                # X = -(x - width // 2) * z / focal_length  
                # Y = -(y - height // 2) * z / focal_length  
                Y = (y - height // 2) * z / focal_length  
                # Z = z  # True depth representation
                Z = -z # True depth representation
                # Z = np.log1p(z) * depth_scale_factor 
                # Z = (depth_map[y, x] / 255.0) * depth_scale_factor * -1  # Invert Z direction

                rotated_point = np.dot(rotation_matrix, [X, Y, Z])
                points.append(rotated_point.tolist())  #


                # points.append([X, Y, Z])
                colors.append(rgb_image[y,x].tolist())  # Ensure proper RGB color mapping


    # Downsample to reduce point count
    sample_indices = np.random.choice(len(points), size=int(len(points) * sample_ratio), replace=False)
    points = np.array(points)[sample_indices]
    colors = np.array(colors)[sample_indices]


    # Convert to VTK format
    poly_data = vtk.vtkPolyData()
    points_vtk = vtk.vtkPoints()
    colors_vtk = vtk.vtkUnsignedCharArray()
    colors_vtk.SetNumberOfComponents(3)  # Ensuring RGB format
    colors_vtk.SetName("Colors")  

    for i, p in enumerate(points):
        points_vtk.InsertNextPoint(p)
        colors_vtk.InsertNextTuple(colors[i])

    poly_data.SetPoints(points_vtk)
    poly_data.GetPointData().SetScalars(colors_vtk)  # Correct color mapping


    # Save as PLY file
    writer = vtk.vtkPLYWriter()
    writer.SetFileName(output_ply)
    writer.SetInputData(poly_data)
    writer.SetArrayName("Colors")  # Ensure Meshlab detects color attributes
    writer.Write()

    print(f"Saved 3D point cloud with fixed depth & color: {output_ply}")



def generate_mesh(input_image_path, input_depth_path, output_ply_folder):
    """
    Generates a PLY file from a single image and depth map pair.
    
    Args:
        input_image_path (str): Path to the input RGB image
        input_depth_path (str): Path to the corresponding depth map
        output_ply_folder (str): Folder to save the generated PLY file
    
    Returns:
        str: Path to the generated PLY file, or None if error
    """
    
    # Create output folder if it doesn't exist
    os.makedirs(output_ply_folder, exist_ok=True)
    
    # Validate input files exist
    if not os.path.exists(input_image_path):
        print(f"Error: Image file not found: {input_image_path}")
        return None
        
    if not os.path.exists(input_depth_path):
        print(f"Error: Depth map file not found: {input_depth_path}")
        return None
    
    # Extract filename without extension from the image path
    image_filename = os.path.basename(input_image_path)
    base_name = os.path.splitext(image_filename)[0]
    
    # Create output PLY path with same name as input image
    output_ply_path = os.path.join(output_ply_folder, f"{base_name}.ply")
    
    try:
        # Call the point cloud generation function
        generate_vtk_point_cloud(input_image_path, input_depth_path, output_ply_path, sample_ratio=0.5)
        
        print(f"Successfully generated PLY file:")
        print(f"  Image: {os.path.basename(input_image_path)}")
        print(f"  Depth: {os.path.basename(input_depth_path)}")
        print(f"  Output: {output_ply_path}")
        
        return output_ply_path
        
    except Exception as e:
        print(f"Error generating PLY file: {e}")
        return None
