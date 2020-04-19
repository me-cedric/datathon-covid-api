# -*-coding:Latin-1 -*

# Extern packages
import numpy
import cv2
import os
from settings import segmentationSettings, classificationSettings


def load_image(path, type):
    return cv2.imread(path, type)


def write_image(img, path):
    if cv2.imwrite(path, img):
        print("File '%s' has been created" % (path))
        return True
    else:
        print("Error during creation of file '%s'" % (path))
        return False


def resize_image(img, width, height, interpolation_type):
    return cv2.resize(img, (width, height), interpolation=interpolation_type)


def segmentation_standardization(input_path):
    # Create writting path
    basename = os.path.basename(input_path)
    [filename, extension] = os.path.splitext(basename)
    writting_path = segmentationSettings['path'] + filename + segmentationSettings['format']

    # Check if file already exists or should be created
    # if os.path.isfile(writting_path):
    #     print("File '%s' already exists" % (writting_path))
    # else:
    img = load_image(input_path, segmentationSettings['color'])
    img = resize_image(
        img,
        segmentationSettings['width'],
        segmentationSettings['height'],
        segmentationSettings['interpolation'],
    )
    if write_image(img, writting_path):
        return writting_path
    return False


def classification_standardization(input_path):
    # Create writting path
    basename = os.path.basename(input_path)
    [filename, extension] = os.path.splitext(basename)
    writting_path = (
        classificationSettings['path'] + filename + classificationSettings['format']
    )

    # Check if file already exists or should be created
    # if os.path.isfile(writting_path):
    #     print("File '%s' already exists" % (writting_path))
    # else:
    img = load_image(input_path, classificationSettings['color'])
    img = resize_image(
        img,
        classificationSettings['width'],
        classificationSettings['height'],
        classificationSettings['interpolation'],
    )
    if write_image(img, writting_path):
        return writting_path
    return False
