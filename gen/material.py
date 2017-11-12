import bpy


def set_smooth(obj, level=None, smooth=True):
    """Sets an objects surface to smooth

    Args:
        obj: Object to smooth
        level (int): Subsurf levels
        smooth (bool): Toggle smooth
    """
    if level:
        # Add subsurf modifier
        modifier = obj.modifiers.new('Subsurf', 'SUBSURF')
        modifier.levels = level
        modifier.render_levels = level

    # Smooth surface
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = smooth


def create_diffuse_material(diffuse_color):
    """Create a simple diffuse material

    Args:
        diffuse_color: Color of material

    Returns:
        Created material
    """
    mat = bpy.data.materials.new('Material')

    # Diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 0.9
    mat.diffuse_color = diffuse_color

    # Specular
    mat.specular_intensity = 0

    return mat


def create_falloff_material(diffuse_color):
    """Create falloff material

    Args:
        diffuse_color: Color of material

    Returns:
        Created material
    """
    mat = bpy.data.materials.new('FalloffMaterial')

    # Diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.use_diffuse_ramp = True
    mat.diffuse_ramp_input = 'NORMAL'
    mat.diffuse_ramp_blend = 'ADD'
    mat.diffuse_ramp.elements[0].color = (1, 1, 1, 1)
    mat.diffuse_ramp.elements[1].color = (1, 1, 1, 0)
    mat.diffuse_color = diffuse_color
    mat.diffuse_intensity = 1.0

    # Specular
    mat.specular_intensity = 0.0

    # Shading
    mat.emit = 0.05
    mat.translucency = 0.2

    return mat