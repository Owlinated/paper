import numpy as np
import os
import time
import datetime
import PIL
import PIL.Image
import tensorflow as tf
from tensorflow._api.v2 import data
from tensorflow.python.data.ops.dataset_ops import AUTOTUNE
from tensorflow.python.framework.ops import Tensor
import tensorflow_datasets as tfds
from matplotlib import pyplot as plt
from IPython import display

BUFFER_SIZE = 400
BATCH_SIZE = 1
IMG_WIDTH = 512
IMG_HEIGHT = 512
OUTPUT_CHANNELS = 1

# Autoencoder with skip connections inspired by https://www.tensorflow.org/tutorials/generative/pix2pix


def parse_pair(path):
    x_file = tf.io.read_file(path[0])
    x_image = tf.image.decode_png(x_file, channels=3)
    x = tf.cast(x_image, tf.float32)

    y_file = tf.io.read_file(path[1])
    y_image = tf.image.decode_png(y_file, channels=1)
    y = tf.cast(y_image, tf.float32)

    return x / 255-0, y / 255.0


def downsample(filters, size, apply_batchnorm=True):
    initializer = tf.random_normal_initializer(0., 0.02)

    result = tf.keras.Sequential()
    result.add(
        tf.keras.layers.Conv2D(filters, size, strides=2, padding='same',
                               kernel_initializer=initializer, use_bias=False))

    if apply_batchnorm:
        result.add(tf.keras.layers.BatchNormalization())

    result.add(tf.keras.layers.LeakyReLU())

    return result


def upsample(filters, size, apply_dropout=False):
    initializer = tf.random_normal_initializer(0., 0.02)

    result = tf.keras.Sequential()
    result.add(
        tf.keras.layers.Conv2DTranspose(filters, size, strides=2,
                                        padding='same',
                                        kernel_initializer=initializer,
                                        use_bias=False))

    result.add(tf.keras.layers.BatchNormalization())

    if apply_dropout:
        result.add(tf.keras.layers.Dropout(0.5))

    result.add(tf.keras.layers.ReLU())

    return result


def Model():
    inputs = tf.keras.layers.Input(shape=[512, 512, 3])

    down_stack = [
        downsample(32, 4, apply_batchnorm=False),  # (bs, 256, 256, 32)
        downsample(64, 4),  # (bs, 128, 128, 64)
        downsample(128, 4),  # (bs, 64, 64, 128)
        downsample(256, 4),  # (bs, 32, 32, 256)
        downsample(512, 4),  # (bs, 16, 16, 512)
        downsample(512, 4),  # (bs, 8, 8, 512)
        downsample(512, 4),  # (bs, 4, 4, 512)
        downsample(512, 4),  # (bs, 2, 2, 512)
        downsample(512, 4),  # (bs, 1, 1, 512)
    ]

    up_stack = [
        upsample(512, 4, apply_dropout=True),  # (bs, 2, 2, 1024)
        upsample(512, 4, apply_dropout=True),  # (bs, 4, 4, 1024)
        upsample(512, 4, apply_dropout=True),  # (bs, 8, 8, 1024)
        upsample(512, 4),  # (bs, 16, 16, 1024)
        upsample(256, 4),  # (bs, 32, 32, 512)
        upsample(128, 4),  # (bs, 64, 64, 256)
        upsample(64, 4),  # (bs, 128, 128, 128)
        upsample(32, 4),  # (bs, 256, 256, 256)
    ]

    initializer = tf.random_normal_initializer(0., 0.02)
    last = tf.keras.layers.Conv2DTranspose(OUTPUT_CHANNELS, 4,
                                           strides=2,
                                           padding='same',
                                           kernel_initializer=initializer,
                                           activation='tanh')  # (bs, 512, 512, 1)

    x = inputs

    # Downsampling through the model
    skips = []
    for down in down_stack:
        x = down(x)
        skips.append(x)

    skips = reversed(skips[:-1])

    # Upsampling and establishing the skip connections
    for up, skip in zip(up_stack, skips):
        x = up(x)
        x = tf.keras.layers.Concatenate()([x, skip])

    x = last(x)

    return tf.keras.Model(inputs=inputs, outputs=x)


def generate_images(model, x, y):
    prediction = model(x, training=True)
    plt.figure(figsize=(15, 15))

    display_list = [x[0], y[0], prediction[0]]
    title = ['Input Image', 'Ground Truth', 'Predicted Image']

    for i in range(3):
        plt.subplot(1, 3, i+1)
        plt.title(title[i])
        plt.imshow(display_list[i])
        plt.axis('off')
    plt.show()


def main():
    path = "../image_generator/training/"
    indexes = [(f"{path}{index:04}x.png", f"{path}{index:04}y.png")
               for index in range(1000)]
    dataset = tf.data.Dataset.from_tensor_slices(indexes)
    dataset = dataset.map(parse_pair, num_parallel_calls=AUTOTUNE)
    dataset = dataset.shuffle(BUFFER_SIZE)
    dataset = dataset.batch(BATCH_SIZE)

    model = Model()
    print(model.summary())

    for example_input, example_target in dataset.take(1):
        generate_images(model, example_input, example_target)

    model.compile("Adam", "BinaryCrossentropy")
    model.fit(dataset)

    for example_input, example_target in dataset.take(1):
        generate_images(model, example_input, example_target)


main()
