import bpy,os,math
from bpy import context, data, ops
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


bpy.context.scene.MPFB_NH_phenotype_gender = 'male'
bpy.ops.mpfb.create_human()
bpy.context.object.rotation_euler[0] = -1.5708
bpy.context.object.location[1] = 1

bpy.context.scene.mpfb_macropanel_age = 0.6578947368421053
bpy.context.scene.mpfb_macropanel_muscle = 0
bpy.context.scene.stomach_stomach_pregnant_decr_incr = 0.5
bpy.context.scene.mpfb_macropanel_weight = 1
if bpy.context.scene.MPFB_NH_phenotype_gender == 'female':
    bpy.context.scene.breast_nipple_point_decr_incr = -1
    bpy.context.scene.breast_nipple_size_decr_incr = 0.02
else:
    bpy.context.scene.breast_nipple_size_decr_incr = 0.07
bpy.context.scene.stomach_stomach_navel_in_out = 0.2
bpy.context.object.scale[0] = 1.0140777857313292
bpy.context.object.scale[1] = 1.0140777857313292
bpy.context.object.scale[2] = 1.0140777857313292
mat = bpy.data.materials.new(name="New_Mat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
texImage.image = bpy.data.images.load('static/images/1.png')
mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
ob = context.view_layer.objects.active

# Assign it to object
if ob.data.materials:
    ob.data.materials[0] = mat  
else:
    ob.data.materials.append(mat)
path = os.path.join(os.path.dirname(
os.path.dirname(os.path.abspath(__file__))), "../../")
bpy.ops.import_scene.gltf(filepath=f'{path}media/backgrounds/default.glb')
bpy.ops.object.select_all(action='SELECT')
name = 'model_7.usdz'
output_path = f'{path}media/models/{name}'

print(path)
bpy.ops.wm.usd_export(
    filepath=output_path,
    export_materials=True
)

print("Done")
