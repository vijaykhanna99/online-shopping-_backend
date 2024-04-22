import bpy, os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


filepaths = ['/home/priyanka/bould-backend/bould_backend/media/clo_3d/female_obs_small.glb','/home/priyanka/bould-backend/bould_backend/media/tryon_models/female_obs.glb']
for i in filepaths:
    print(i)
    bpy.ops.import_scene.gltf(filepath=i)

path = os.path.join(os.path.dirname(
os.path.dirname(os.path.abspath(__file__))), "../../")

name = 'kinny Jeans_f_obs_small.usdz'
output_path = f'{path}media/combinations/{name}'

bpy.ops.wm.usd_export(
    filepath=output_path,
    export_materials=True
)