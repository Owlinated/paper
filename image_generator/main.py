import os
import tempfile
from threading import Thread

import numpy as np
import zmq
from PIL import Image
from bpy_extras.object_utils import world_to_camera_view

import bpy
import generator
import util

# We use 0MQ to send the rendered images
socket = zmq.Context().socket(zmq.PUSH)
# Limit number of buffered messages
socket.set_hwm(8)
socket.connect('ipc:///tmp/paper-tensor-ipc')

# We use FIFO to trick blender into rendering into memory
fifo_dir = tempfile.mkdtemp()
file_path = os.path.join(fifo_dir, 'fifo.bmp')
os.mkfifo(file_path)

# Keep track of thread and current label
thread = None
label = None


def threaded_send_image():
    """Send image from fifo to tensor flow
    """
    global label
    image_parsed = Image.open(file_path)
    image = np.array(image_parsed)

    print('Image:')
    print(image.shape)
    print(image.dtype)
    print('Label:')
    print(label)
    print(label.shape)
    print(label.dtype)

    # 480x640x3 uint8
    socket.send(image, copy=False, track=False)
    # 4x2 float64
    socket.send(label, copy=False, track=False)


def reset_render_scene():
    global label, thread

    # Reset scene
    scene = bpy.context.scene
    util.remove_all()
    util.setup_scene(640, 480)
    scene.cursor_location = (0, 0, 0)

    paper_to_world = generator.setup_scene()

    # Wait for last image to be sent
    if thread is not None:
        thread.join()

    # Find label for training
    def drop_y(camera): return (camera[0], camera[1])

    def to_camera(world_vector): return world_to_camera_view(scene, scene.camera, world_vector)

    label = np.array(list(map(drop_y, map(to_camera, map(paper_to_world, [(0, 0), (0, 1), (1, 0), (1, 1)])))))

    # Render scene to fifo
    thread = Thread(target=threaded_send_image)
    thread.start()
    util.render_scene(file_path)


while True: reset_render_scene()
