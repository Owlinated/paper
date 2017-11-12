import bpy


def setup_scene(res_x=800, res_y=800, res_percentage=100):
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


def set_ambient_occlusion(ambient_occlusion=True, samples=5, blend_type='ADD'):
    """Configure ambient occlusion

    Args:
        ambient_occlusion (bool): Toggle ambient occlusion
        samples: Number of occlusion samples
        blend_type: Sample blend type ('ADD', 'MULTIPLY')
    """
    bpy.context.scene.world.light_settings.use_ambient_occlusion = ambient_occlusion
    bpy.context.scene.world.light_settings.ao_blend_type = blend_type
    bpy.context.scene.world.light_settings.samples = samples


def remove_all():
    """Remove all elements in scene
    """
    bpy.ops.object.select_by_layer()
    bpy.ops.object.delete(use_global=False)


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
    constraint.up_axis = 'UP_Y'
    # constraint.owner_space = 'LOCAL'
    # constraint.target_space = 'LOCAL'

    return constraint


def create_target(origin=(0, 0, 0)):
    """Creates a target at specified location

    Args:
        origin: location of target

    Returns:
        Created target
    """
    tar = bpy.data.objects.new('Target', None)
    bpy.context.scene.objects.link(tar)
    tar.location = origin

    return tar


def create_camera(origin, target=None, lens=35, clip_start=0.1, clip_end=200, type='PERSP', ortho_scale=6):
    """Create camera and matching object

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
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    cam.clip_start = clip_start
    cam.clip_end = clip_end
    cam.type = type
    if type == 'ORTHO':
        cam.ortho_scale = ortho_scale

    # Link object to scene
    obj = bpy.data.objects.new("CameraObj", cam)
    obj.location = origin
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.camera = obj

    if target: track_to_constraint(obj, target)
    return obj


def create_light(origin, type='POINT', energy=1, color=(1, 1, 1), target=None):
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
    print('createLamp called')
    bpy.ops.object.add(type='LAMP', location=origin)
    obj = bpy.context.object
    obj.data.type = type
    obj.data.energy = energy
    obj.data.color = color

    if target: track_to_constraint(obj, target)
    return obj


def render_scene(render_name='render'):
    # Assert folder exists
    """Render scene to file

    Args:
        render_name: Output file name
    """
    bpy.context.scene.render.filepath = render_name + '.png'
    bpy.ops.render.render(write_still=True)
