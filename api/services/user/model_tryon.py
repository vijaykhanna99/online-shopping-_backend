import bpy,os
from mathutils import Quaternion

bpy.context.scene.cycles.device = 'GPU'
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
bpy.context.preferences.addons['cycles'].preferences.devices[0].use = True
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


filepaths = ['/home/priyanka/bould-backend/bould_backend/media/clo_3d/m_small_s_RTqhLPZ.glb', '/home/priyanka/bould-backend/bould_backend/media/clo_3d/m_small_s_6tjC4NC.glb', '/home/priyanka/bould-backend/bould_backend/media/tryon_models/male_small.glb', '/home/priyanka/bould-backend/bould_backend/media/backgrounds/default.glb']
for i in filepaths:
    print(i)
    bpy.ops.import_scene.gltf(filepath=i)

path = os.path.join(os.path.dirname(
os.path.dirname(os.path.abspath(__file__))), "../../")

name = 'base_12.usdz'
output_path = f'{path}media/tryon_models/{name}'

bpy.ops.wm.usd_export(
    filepath=output_path,
    export_materials=True
)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()