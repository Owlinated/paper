import random

import bpy

import material
import mathutils
import paper
import util


def rand():
    """Boring random number generator: gauss around 0.5
    """
    return random.gauss(.5, .5)


def setup_scene(paper_resolution=20):
    # Create camera
    target = util.create_target()
    util.update_camera((0, 0, 10), target)

    # Create lamps
    util.create_light(origin=(0, 0, 10), type='POINT', energy=rand(), color=(rand(), rand(), rand()))
    util.set_ambient_occlusion()

    # Create backdrop
    cubesize = 5
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, -cubesize))
    cube = bpy.context.scene.objects['Cube']
    cube.scale = (cubesize, cubesize, cubesize)
    cube_material = material.create_diffuse_material((rand(), rand(), rand()))
    cube.data.materials.append(cube_material)

    # Create paper
    paperGen = paper.create_random_paper()
    minHeight, mesh = paper.generate(paper_resolution, paper_resolution, paperGen)
    material.set_smooth(mesh)

    # Return lambda that maps paper coordinates to world
    def adjust_height(world): return mathutils.Vector((world[0], world[1], world[2] - minHeight))

    return lambda coord: adjust_height(paperGen(*coord))

    # TODO
    # Setup scene (backdrop, sheet, camera)
    # Repeat x times
    # Randomize scene (Mostly normal distribution)
    # Random background texture (solid, textures)
    # Random backdrop material (glossy, matte)
    # Random lights
    # Count
    # Type
    # Position
    # Color
    # Direction
    # Random sheet textures
    # Random surface
    # Random camera position
    # Lookat position
    # Distance from sheet
    # Position on half spehere
    # Rotation around lookat axis
    # Random camera parameters (start with fixed to iphone 6s plus)
    # Render image
    # Keep track of surface parameters and edge positions
    # Create tfrecord file
