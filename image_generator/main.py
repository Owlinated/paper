import os
import random
import tempfile
from threading import Thread

import numpy as np
import zmq
from PIL import Image
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

# We use 0MQ to send the rendered images
ctx = zmq.Context()
socket = ctx.socket(zmq.PUSH)
socket.connect('ipc:///tmp/paper-tensor-ipc')

# We use FIFO to trick blender into rendering into memory
fifo_dir = tempfile.mkdtemp()
filepath = os.path.join(fifo_dir, 'fifo.bmp')
os.mkfifo(filepath)

# TODO proper thread design i.e. concurrent rendering & sending
# We use a thread to have a reader open when blender tries to write to FIFO
thread = None
# Keep track of image labels, so the thread can access them
label = None


def threaded_send_image():
    """Send image from fifo to tensor flow
    """
    image_parsed = Image.open(filepath)
    image = np.array(image_parsed)

    print(image.shape)
    print(image.dtype)
    print(label.shape)
    print(label.dtype)

    # 480x640x3 uint8
    socket.send(image, copy = False, track = False)
    # 4x2 float64
    socket.send(label, copy = False, track = False)


def rand():
    """Boring random number generator: gauss around 0.5
    """
    return random.gauss(.5, .5)


while True:
    # Reset scene
    util.remove_all()
    util.setup_scene(640, 480)

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
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, -cubesize))
    cube = bpy.context.scene.objects['Cube']
    cube.scale = (cubesize, cubesize, cubesize)
    cube_material = material.create_diffuse_material((rand(), rand(), rand()))
    cube.data.materials.append(cube_material)

    # Create paper
    paperGen = paper.create_random_paper()
    minHeight, mesh = paper.generate(20, 20, paperGen)
    material.set_smooth(mesh)

    # Wait for last image to be sent
    if thread is not None:
        thread.join()

    # Find labels for training
    scene = bpy.context.scene
    cam = scene.camera
    label = np.array(list(map(lambda camera: (camera[0], camera[1]),
                map(lambda world_vector: world_to_camera_view(scene, cam, world_vector),
                    map(lambda world: mathutils.Vector((world[0], world[1], world[2] - minHeight)),
                        map(lambda coord: paperGen(*coord), [(0, 0), (0, 1), (1, 0), (1, 1)]))))))
    print('Label:')
    print(label)

    # Render scene to fifo
    thread = Thread(target=threaded_send_image)
    thread.start()
    util.render_scene(filepath)
