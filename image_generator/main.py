import random

from bpy_extras.object_utils import world_to_camera_view

import bpy
import material
import mathutils
import paper
import util

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

# Reset scene
util.remove_all()
util.setup_scene(640, 480)

def rand(): return random.gauss(.5,.5)

# Set cursor to (0, 0, 0)
bpy.context.scene.cursor_location = (0, 0, 0)

# Create camera
target = util.create_target()
camera = util.create_camera((0, 0, 10), target)

# Create lamps
util.create_light(origin=(0, 0, 10), type='POINT', energy=rand(), color=(rand(), rand(), rand()))
util.set_ambient_occlusion()

# Create backdrop
cubesize = 5
bpy.ops.mesh.primitive_cube_add(location=(0,0,-cubesize))
cube = bpy.context.scene.objects['Cube']
cube.scale = (cubesize, cubesize, cubesize)
cube_material = material.create_diffuse_material((rand(),rand(),rand()))
cube.data.materials.append(cube_material)

# Create paper
paperGen = paper.create_random_paper()
minHeight, mesh = paper.generate(20, 20, paperGen)
material.set_smooth(mesh)

# Render scene
util.render_scene('paper')

# Find labels for training
scene = bpy.context.scene
cam = scene.camera
print('Labels:')
coordinates = [(0, 0), (0, 1), (1, 0), (1, 1)]
for coord in coordinates:
    world = paperGen(*coord)
    world = mathutils.Vector((world[0], world[1], world[2] - minHeight))
    screen = world_to_camera_view(scene, cam, world)
    print('{}: ({:<5.3}, {:<5.3})'.format(coord, screen.x, screen.y, prec='.3'))
