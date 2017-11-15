import numpy as np
import tensorflow as tf
import zmq

num_batches = 10
batch_size = 10

# We use 0MQ to receive datasets
socket = zmq.Context().socket(zmq.PULL)
socket.bind('ipc:///tmp/paper-tensor-ipc')


# This generator receives data points
def generator():
    while True:
        image_message = socket.recv(copy=False, track=False)
        image = np.frombuffer(image_message, np.uint8)\
            .astype(np.float32).reshape((480, 640, 3))

        label_message = socket.recv(copy=False, track=False)
        label = np.frombuffer(label_message, np.float64)\
            .astype(np.float32).reshape((4, 2))

        yield image, label


dataset = tf.data.Dataset.from_generator(
    generator,
    (tf.float32, tf.float32),
    (tf.TensorShape([480,640,3]), tf.TensorShape([4,2]))
)

image, label = dataset.make_one_shot_iterator().get_next()
session = tf.Session()
session.run([image, label])

#TODO define some NN that uses the dataset
