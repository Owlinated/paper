import numpy as np
from bpy_extras.object_utils import world_to_camera_view

import bpy
import generator
import util

# This demo sets up a single scene. Use for debuggin in blender

scene = bpy.context.scene
util.remove_all()
util.setup_scene(640, 480)
scene.cursor_location = (0, 0, 0)

paper_to_world = generator.setup_scene()

# Find label for training
def drop_y(camera): return (camera[0], camera[1])

def to_camera(world_vector): return world_to_camera_view(scene, scene.camera, world_vector)

label = np.array(list(map(drop_y, map(to_camera, map(paper_to_world, [(0, 0), (0, 1), (1, 0), (1, 1)])))))
print('Label:')
print(label)
