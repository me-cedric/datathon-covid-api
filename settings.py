# -*-coding:Latin-1 -*

# Extern packages
import numpy
import cv2

class SegmentationSettings :
	path   = "images/ready_for_segmentation/"
	width  = 512
	height = 512
	format = ".png"
	color  = cv2.IMREAD_GRAYSCALE
	interpolation = cv2.INTER_AREA	

class ClassificationSettings :
	path   = "images/ready_for_classification/"
	width  = 128
	height = 128
	format = ".jpg"
	color  = cv2.IMREAD_GRAYSCALE
	interpolation = cv2.INTER_AREA	

