import numpy as np
from bpy_extras.object_utils import world_to_camera_view

import bpy
import importlib
import generator
import util

# Force reload to apply changes
importlib.reload(generator)
importlib.reload(util)

# This demo sets up a single scene. Use for debugging in blender
util.setup_scene()
paper_to_world = generator.setup_scene()


def drop_y(camera): return (camera[0], camera[1])


def to_camera(world_vector): return world_to_camera_view(
    bpy.context.scene, bpy.context.scene.camera, world_vector)


# Find label for training
label = np.array(list(map(drop_y, map(to_camera, map(
    paper_to_world, [(0, 0), (0, 1), (1, 0), (1, 1)])))))
print('Label:')
print(label)
