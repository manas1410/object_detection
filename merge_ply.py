import vtk

INPUT_PLY = 'output_ply'

def transform_object_ply(object_ply, translation):
    """Applies a translation to the object PLY file before merging."""
    
    # Load object PLY
    reader = vtk.vtkPLYReader()
    reader.SetFileName(object_ply)
    reader.Update()
    poly_data = reader.GetOutput()

    # Apply translation
    transform = vtk.vtkTransform()
    transform.Translate(*translation)

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetTransform(transform)
    transform_filter.SetInputData(poly_data)
    transform_filter.Update()

    return transform_filter.GetOutput()

def extract_colors(poly_data):
    """Extracts RGB colors from the PLY file and ensures proper formatting for VTK."""
    color_array = poly_data.GetPointData().GetScalars()

    if not color_array:
        print("⚠ Warning: No color data found in PLY file.")
        return None

    formatted_colors = vtk.vtkUnsignedCharArray()
    formatted_colors.SetNumberOfComponents(3)
    formatted_colors.SetName("Colors")

    for i in range(color_array.GetNumberOfTuples()):
        color_tuple = color_array.GetTuple(i)
        formatted_colors.InsertNextTuple3(int(color_tuple[0]), int(color_tuple[1]), int(color_tuple[2]))

    return formatted_colors

def merge_ply_files(base_ply, object_ply, output_ply, translation=(0, 0, 0)):
    """Merges two PLY files while correctly retaining RGB colors."""
    

    base_reader = vtk.vtkPLYReader()
    base_reader.SetFileName(base_ply)
    base_reader.Update()
    base_poly_data = base_reader.GetOutput()

    object_reader = vtk.vtkPLYReader()
    object_reader.SetFileName(object_ply)
    object_reader.Update()
    object_poly_data = object_reader.GetOutput()


    transform = vtk.vtkTransform()
    transform.Translate(*translation)

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetTransform(transform)
    transform_filter.SetInputData(object_poly_data)
    transform_filter.Update()
    transformed_object_poly_data = transform_filter.GetOutput()


    base_colors = extract_colors(base_poly_data)
    object_colors = extract_colors(transformed_object_poly_data)


    append_filter = vtk.vtkAppendPolyData()
    append_filter.AddInputData(base_poly_data)
    append_filter.AddInputData(transformed_object_poly_data)
    append_filter.Update()
    merged_poly_data = append_filter.GetOutput()


    merged_color_array = vtk.vtkUnsignedCharArray()
    merged_color_array.SetNumberOfComponents(3)
    merged_color_array.SetName("Colors")

    if base_colors:
        for i in range(base_colors.GetNumberOfTuples()):
            merged_color_array.InsertNextTuple3(*base_colors.GetTuple(i))

    if object_colors:
        for i in range(object_colors.GetNumberOfTuples()):
            merged_color_array.InsertNextTuple3(*object_colors.GetTuple(i))

    merged_poly_data.GetPointData().SetScalars(merged_color_array)

    writer = vtk.vtkPLYWriter()
    writer.SetFileName(output_ply)
    writer.SetInputData(merged_poly_data)
    writer.SetArrayName("Colors")  
    writer.SetFileTypeToBinary()  
    writer.Write()

    print(f"✅ Merged PLY saved with correct per-vertex RGB colors: {output_ply}")


def check_ply_colors(ply_file):
    """Checks if a PLY file has RGB color information."""
    reader = vtk.vtkPLYReader()
    reader.SetFileName(ply_file)
    reader.Update()

    poly_data = reader.GetOutput()
    color_array = poly_data.GetPointData().GetArray("Colors")


    if color_array:
        poly_data.GetPointData().SetScalars(color_array)  
    else:
        print(f"⚠ Warning: No color data found in ")


def check_ply_data(ply_file):
    """Prints debugging info about a PLY file: vertex count & color attributes."""
    reader = vtk.vtkPLYReader()
    reader.SetFileName(ply_file)
    reader.Update()
    poly_data = reader.GetOutput()


    num_points = poly_data.GetNumberOfPoints()
    print(f"✅ {ply_file} has {num_points} vertices.")


    color_array = poly_data.GetPointData().GetArray("Colors")  

    if not color_array:
        color_array = poly_data.GetPointData().GetArray("diffuse_red") 
        color_array = poly_data.GetPointData().GetArray("RGB")

    if color_array:
        print(f"✅ {ply_file} contains color data!")
        print(f"Sample Colors: {color_array.GetTuple(0)}")  
    else:
        print(f"⚠ {ply_file} does NOT contain recognized color attributes.")



# check_ply_data("C:\\Users\\ASUS Zenbook A14\\Downloads\\output_ply\\test\\WhatsApp Image 2025-06-15 at 12.49.26 AM.ply")
# check_ply_data("C:\\Users\\ASUS Zenbook A14\\Downloads\\output_ply\\test\\WhatsApp Image 2025-06-15 at 12.49.25 AM.ply")


# merge_ply_files(
#     "C:\\Users\\ASUS Zenbook A14\\Downloads\\output_ply\\test\\WhatsApp Image 2025-06-15 at 12.49.26 AM.ply",
#     "C:\\Users\\ASUS Zenbook A14\\Downloads\\output_ply\\test\\WhatsApp Image 2025-06-15 at 12.49.25 AM.ply",
#     "C:\\Users\\ASUS Zenbook A14\\Downloads\\output_ply\\test\\merged_scene.ply",
#     translation=(0, 0, 0)  
# )
