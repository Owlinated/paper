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

# Set cursor to (0, 0, 0)
bpy.context.scene.cursor_location = (0, 0, 0)

# Create camera
target = util.create_target()
camera = util.create_camera((0, 0, 10), target)

# Create lamps
#utils.rainbowLights(10, 300, 3)
util.create_light((0, 0, 10))
util.set_ambient_occlusion()

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
