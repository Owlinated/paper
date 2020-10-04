import numpy as np
from bpy_extras.object_utils import world_to_camera_view

import bpy
import os
import generator
import util
# This script renders random scenes in a loop


def reset_render_scene(index):
    # Reset scene
    util.setup_scene()

    paper_to_world = generator.setup_scene()

    # Find label for training
    def drop_y(camera): return (camera[0], camera[1])

    def to_camera(world_vector): return world_to_camera_view(
        bpy.context.scene, bpy.context.scene.camera, world_vector)

    label = np.array(list(map(drop_y, map(to_camera, map(
        paper_to_world, [(0, 0), (0, 1), (1, 0), (1, 1)])))))

    # Render scene to fifo
    util.render_scene(f'{os.getcwd()}/training/{index}.png')


index = 0
while True:
    reset_render_scene(index)
    index += 1
