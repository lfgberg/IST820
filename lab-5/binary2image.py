import os, math
import argparse
from PIL import Image
from queue import Queue
from threading import Thread
import json
import pdb
import glob
import config
import numpy as np
import multiprocessing
import tensorflow as tf


def getBinaryData(filename):
    """
    Extract byte values from binary executable file and store them into list
    :param filename: executable file name
    :return: byte value list
    """

    binary_values = []

    with open(filename, "rb") as fileobject:

        # read file byte by byte
        data = fileobject.read(1)

        while data != b"":
            binary_values.append(ord(data))
            data = fileobject.read(1)

    return binary_values


def createGreyScaleImage(filename, width=64):
    """
    Create greyscale image from binary data. Use given with if defined or create square size image from binary data.
    :param filename: image filename
    """
    greyscale_data = getBinaryData(filename)
    size = get_size(len(greyscale_data), width)
    print(size)
    save_file(filename, greyscale_data, size, "L")


def createRGBImage(filename, width=64):
    """
    Create RGB image from 24 bit binary data 8bit Red, 8 bit Green, 8bit Blue
    :param filename: image filename
    """
    index = 0
    rgb_data = []

    # Read binary file
    binary_data = getBinaryData(filename)

    # Create R,G,B pixels
    while (index + 3) < len(binary_data):
        R = binary_data[index]
        G = binary_data[index + 1]
        B = binary_data[index + 2]
        index += 3
        rgb_data.append((R, G, B))

    size = get_size(len(rgb_data), width)
    print(size)
    save_file(filename, rgb_data, size, "RGB")


def getGreyScaleImage(fns, width=64):
    # ßif (isinstance(fns, multiprocessing.managers.ListProxy) or
    if isinstance(fns, list) == False and isinstance(fns, tuple) == False:
        fns = [fns]
    imgs = []
    for filename in fns:
        greyscale_data = getBinaryData(filename)
        size = get_size(len(greyscale_data), width)
        image = Image.new("L", size)
        image.putdata(greyscale_data)
        # _img = image.resize((config.img_height, config.img_width))
        stacked_img = np.stack((image,), axis=-1)
        stacked_img = tf.image.resize(
            stacked_img, (config.img_height, config.img_width), method="bilinear"
        )
        # img = tf.io.read_file("tmp.png")
        # img = tf.image.decode_image(img,channels=3, expand_animations=False)
        # img = tf.image.resize(img,(32,32),method='bilinear')
        imgs.append(stacked_img)
    return imgs


def getRGBImage(filename, width=64):
    if isinstance(fns, list) == False:
        fns = [fns]
    imgs = []
    for filename in fns:
        index = 0
        rgb_data = []

        # Read binary file
        binary_data = getBinaryData(filename)

        # Create R,G,B pixels
        while (index + 3) < len(binary_data):
            R = binary_data[index]
            G = binary_data[index + 1]
            B = binary_data[index + 2]
            index += 3
            rgb_data.append((R, G, B))

        size = get_size(len(rgb_data), width)
        image = Image.new("RGB", size)
        image.putdata(rgb_data)
        stacked_img = np.stack((image,) * 3, axis=-1)
        stacked_img = tf.image.resize(stacked_img, (32, 32), method="bilinear")
        imgs.append(stacked_img)
    return imgs


def save_file(filename, data, size, image_type):

    try:
        image = Image.new(image_type, size)
        image.putdata(data)

        # setup output filename
        dirname = "images"
        name, _ = os.path.splitext(filename)
        name = os.path.basename(name)

        if filename.find("Virus") != -1:
            imagename = (
                dirname + os.sep + "Virus" + os.sep + name + "_" + image_type + ".png"
            )
        else:
            imagename = (
                dirname + os.sep + "Benign" + os.sep + name + "_" + image_type + ".png"
            )

        os.makedirs(os.path.dirname(imagename), exist_ok=True)

        image.save(imagename)
        print("The file", imagename, "saved.")
    except Exception as err:
        print(err)
        pdb.set_trace()


def get_size(data_length, width=64):
    # source Malware images: visualization and automatic classification by L. Nataraj
    # url : http://dl.acm.org/citation.cfm?id=2016908

    if width is None:  # with don't specified any with value

        size = data_length

        if size < 10240:
            width = 32
        elif 10240 <= size <= 10240 * 3:
            width = 64
        elif 10240 * 3 <= size <= 10240 * 6:
            width = 128
        elif 10240 * 6 <= size <= 10240 * 10:
            width = 256
        elif 10240 * 10 <= size <= 10240 * 20:
            width = 384
        elif 10240 * 20 <= size <= 10240 * 50:
            width = 512
        elif 10240 * 50 <= size <= 10240 * 100:
            width = 768
        else:
            width = 1024

        height = int(size / width) + 1

    else:
        height = width
        width = int(data_length / width) + 1  # int(math.sqrt(data_length)) + 1
    print(width, height)
    return (width, height)


def run(file_queue, width):
    while not file_queue.empty():
        filename = file_queue.get()
        print(file_queue.qsize(), filename)
        createGreyScaleImage(filename, width)
        createRGBImage(filename, width)
        file_queue.task_done()


def main(width=None, thread_number=7):
    # Get all executable files in input directory and add them into queue
    # files = ['result_Virus_bb.out']
    files = glob.glob("data/binary/Benign/*") + glob.glob("data/binary/Virus/*")
    file_queue = Queue()
    for f in files:
        f2 = f.split("/")[-1]
        # f = 'data/binary/'+f.split('CFG_hex/')[-1]
        file_queue.put(f)
    for index in range(thread_number):
        thread = Thread(target=run, args=(file_queue, width))
        thread.daemon = True
        thread.start()
    file_queue.join()


def getfile():
    filename = "data/binary/Tmp/Virus/VirusShare_1e94d6593bec08d8ef4d051d7271385c"
    createGreyScaleImage(filename, 64)


if __name__ == "__main__":
    # getfile()
    main(width=None)
