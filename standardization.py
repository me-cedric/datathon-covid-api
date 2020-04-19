# -*-coding:Latin-1 -*

# Extern packages
import numpy
import cv2
import os
from settings import SegmentationSettings
from settings import ClassificationSettings


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
    writting_path = SegmentationSettings.path + filename + SegmentationSettings.format

    # Check if file already exists or should be created
    # if os.path.isfile(writting_path):
    #     print("File '%s' already exists" % (writting_path))
    # else:
    img = load_image(input_path, SegmentationSettings.color)
    img = resize_image(
        img,
        SegmentationSettings.width,
        SegmentationSettings.height,
        SegmentationSettings.interpolation,
    )
    if write_image(img, writting_path):
        return writting_path
    return False


def classification_standardization(input_path):
    # Create writting path
    basename = os.path.basename(input_path)
    [filename, extension] = os.path.splitext(basename)
    writting_path = (
        ClassificationSettings.path + filename + ClassificationSettings.format
    )

    # Check if file already exists or should be created
    # if os.path.isfile(writting_path):
    #     print("File '%s' already exists" % (writting_path))
    # else:
    img = load_image(input_path, ClassificationSettings.color)
    img = resize_image(
        img,
        ClassificationSettings.width,
        ClassificationSettings.height,
        ClassificationSettings.interpolation,
    )
    if write_image(img, writting_path):
        return writting_path
    return False
