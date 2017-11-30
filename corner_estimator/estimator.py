import numpy as np
import tensorflow as tf
import zmq

# Training Parameters
num_steps = 100
display_step = 10
batch_size = 3

# Network Parameters
num_input = 784  # MNIST data input (img shape: 28*28)
num_classes = 10  # MNIST total classes (0-9 digits)
dropout = 0.75  # Dropout, probability to keep units

# We use 0MQ to receive datasets
socket = zmq.Context().socket(zmq.PULL)
socket.bind('ipc:///tmp/paper-tensor-ipc')


# This generator receives data points
def generator():
    while True:
        image_message = socket.recv(copy=False, track=False)
        image = np.frombuffer(image_message, np.uint8) \
            .astype(np.float32).reshape((480, 640, 3))

        label_message = socket.recv(copy=False, track=False)
        label = np.frombuffer(label_message, np.float64) \
            .astype(np.float32).reshape((4, 2))

        yield image, label


# Pick inputs from the generator
dataset = tf.data.Dataset.from_generator(
    generator,
    (tf.float32, tf.float32),
    (tf.TensorShape([480, 640, 3]), tf.TensorShape([4, 2]))
)
image, label = dataset \
    .prefetch(3 * batch_size).batch(batch_size) \
    .make_one_shot_iterator().get_next()


# TODO Refactor this with placeholder for inputs
# TODO experiment with dropout in case of training - but can you really overfit generated stuff?
def net():
    conv1 = tf.layers.conv2d(image, 32, 5, activation=tf.nn.relu)
    pool1 = tf.layers.max_pooling2d(conv1, 5, 5)

    conv2 = tf.layers.conv2d(pool1, 32, 5, activation=tf.nn.relu)
    pool2 = tf.layers.max_pooling2d(conv2, 5, 5)

    conv3 = tf.layers.conv2d(pool2, 32, 3, activation=tf.nn.relu)
    pool3 = tf.layers.max_pooling2d(conv3, 5, 5)

    flat1 = tf.contrib.layers.flatten(pool3)
    fc1 = tf.layers.dense(flat1, 8, activation=tf.nn.relu)

    # Output layer, corner coordinates (4 corners in 2D)
    prediction = tf.layers.dense(fc1, 8)

    # Define loss as mean square error
    shaped_label = tf.reshape(label, [batch_size, 8])
    loss = tf.reduce_sum(tf.pow(prediction - shaped_label, 2)) / (8 * batch_size)
    return prediction, loss


# Setup network
train_prediction, train_loss = net()

optimizer = tf.train.AdamOptimizer().minimize(train_loss)

init = tf.global_variables_initializer()

# Start training
with tf.Session() as sess:
    # Run the initializer
    sess.run(init)

    # Fit all training data
    for epoch in range(num_steps):
        sess.run(optimizer)

        # Display logs per epoch step
        if (epoch + 1) % display_step == 0:
            result = sess.run([train_loss, train_prediction, label])
            print("Epoch:", '%04d' % (epoch + 1), "loss=", "{:.9f}".format(result[0]))
            print("Prediction:")
            print(np.reshape(result[1], [batch_size, 4, 2]))
            print("Label:")
            print(result[2])

    print("Optimization Finished!")
    print("Training cost=", sess.run(train_loss))

    # TODO setup tests with real examples
