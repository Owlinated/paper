import bpy
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper

import random

import paper


def rand():
    """Boring random number generator: gauss around 0.5
    """
    return random.gauss(.5, .5)


def setup_scene(res_x=512, res_y=512, res_percentage=100):
    """Setup scene rendering options

    Args:
        res_x: Horizontal resolution
        res_y: Vertical resolution
        res_percentage: Resolution scale
    """
    scene = bpy.context.scene

    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = res_percentage
    scene.cursor.location = (0, 0, 0)

    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.use_ambient_occlusion = True
    scene.cycles.samples = 512
    scene.cycles.use_adaptive_sampling = True


def track_to_constraint(obj, target):
    """Setup tracking constraint for object

    Args:
        obj: Object to create constraint for
        target: Tracking target for constraint

    Returns:
        Created constraint

    """
    constraint = obj.constraints.new('TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    # constraint.track_axis = 'TRACK_Z'
    constraint.up_axis = 'UP_X'
    # constraint.owner_space = 'LOCAL'
    # constraint.target_space = 'LOCAL'

    return constraint


def ensure_target(origin=(0, 0, 0)):
    """Creates a target at specified location

    Args:
        origin: location of target

    Returns:
        Created target
    """
    target = bpy.data.objects.get('Target', None)
    if (target is None):
        target = bpy.data.objects.new('Target', None)
        bpy.context.scene.collection.objects.link(target)
    target.location = origin

    return target


def ensure_camera(origin, target=None, lens=35, clip_start=0.1, clip_end=200, type='PERSP', ortho_scale=6):
    """Update camera and matching object

        Args:
            origin: Location of camera
            target: Target for camera constraint
            lens: Camera lens size
            clip_start: Near clipping plane distance
            clip_end: Far clipping plane distance
            type: Camera perspective type ('PERSP', 'ORTHO', 'PANO')
            ortho_scale: Zoom for orthographic perspective type

        Returns:
            Created camera
        """
    obj = bpy.context.scene.camera
    if (obj is None):
        cam = bpy.data.cameras.new("Camera")
        obj = bpy.data.objects.new("CameraObj", cam)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.scene.camera = obj
    cam = obj.data

    # Update camera
    cam.lens = lens
    cam.clip_start = clip_start
    cam.clip_end = clip_end
    cam.type = type
    if type == 'ORTHO':
        cam.ortho_scale = ortho_scale

    # Update object
    obj.location = origin
    obj.rotation_euler[2] = 90

    if target is not None:
        track_to_constraint(obj, target)


def ensure_cube(cubesize=8):
    cube = bpy.context.scene.objects.get('Cube')
    if cube is None:
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object

    cube.location = (0, 0, -cubesize)
    cube.scale = (cubesize, cubesize, cubesize)

    cube_material = bpy.data.materials.get('CubeMaterial')
    if (cube_material is None):
        cube_material = bpy.data.materials.new('CubeMaterial')
    cube_material.use_nodes = True
    principled = PrincipledBSDFWrapper(cube_material, is_readonly=False)
    principled.base_color = (rand(), rand(), rand())
    cube.data.materials.append(cube_material)


def ensure_paper(paperGen, paper_resolution=20):
    obj = bpy.context.scene.objects.get('Paper')
    if obj is not None:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.delete()

    minHeight, paper_mesh = paper.generate(
        paper_resolution, paper_resolution, paperGen)

    paper_material = bpy.data.materials.get('PaperMaterial')
    if (paper_material is None):
        paper_material = bpy.data.materials.new('PaperMaterial')
    paper_material.use_nodes = True
    principled = PrincipledBSDFWrapper(paper_material, is_readonly=False)
    principled.base_color = (rand(), rand(), rand())
    paper_mesh.data.materials.append(paper_material)

    return minHeight


def ensure_light(origin, type='POINT', energy=rand(), color=(rand(), rand(), rand()), target=None):
    """Create a light

    Args:
        origin: Light location
        type: Light type ('POINT', 'SUN', 'SPOT', 'HEMI', 'AREA')
        energy: Intensity of light
        color: Color of light
        target: Target for light constraint

    Returns:
        Created light
    """
    obj = bpy.context.scene.objects.get('Light')
    if (obj is None):
        bpy.ops.object.add(type='LIGHT', location=origin)
        obj = bpy.context.object

    obj.data.type = type
    obj.data.energy = energy
    obj.data.color = color

    if target:
        track_to_constraint(obj, target)

    return obj


def render_scene(filepath, file_format='PNG'):
    # Assert folder exists
    """Render scene to file

    Args:
        render_name: Output file name
    """
    render = bpy.context.scene.render
    render.image_settings.file_format = file_format
    render.filepath = filepath
    bpy.ops.render.render(write_still=True)
