import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
# Clear existing data in Blender
# bpy.ops.wm.read_factory_settings(use_empty=True)
size = ['skn','avg','fat','obs']
# gender = ['male','female']
gender = ['female', 'male']

for i in gender:
    for j in size:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        # name = "tshirt/{i}_{j}"
        name = f"eye_tshirt/{i}_{j}_medium"
        # Set the path to your OBJ file
        obj_file_path = f"/home/priyanka/Desktop/practice-project/{name}.glb"
        print(obj_file_path)
        # Import OBJ file   
        # bpy.ops.wm.obj_import(filepath=obj_file_path)
        bpy.ops.import_scene.gltf(filepath=obj_file_path)

        # scale = 0.010008
        scale = 0.001
        scale_factors = (scale, scale, scale) 
        bpy.ops.transform.resize(value=scale_factors)
        bpy.ops.object.mode_set(mode='EDIT')

        # Get the active object and its mesh data
        obj = bpy.context.edit_object
        mesh = bpy.context.edit_object.data

        # Ensure we're in vertex select mode
        bpy.ops.mesh.select_all(action='SELECT')

        # Move vertices along the X-axis
        bpy.ops.transform.translate(value=(0.0, 0.0, -1))
        bpy.context.object.rotation_mode = "XYZ"
        bpy.context.object.rotation_euler[0] = 0
        bpy.context.object.location[1] = 1

        # Switch back to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # Set the path for the USD export
        output_path = f"/home/priyanka/Desktop/practice-project/{name}.gltf"

        # Select all objects in the scene
        bpy.ops.object.select_all(action='SELECT')


        bpy.ops.export_scene.gltf(filepath=output_path)

        # Print a message indicating the successful export
        print(f"Exported to {output_path}")
