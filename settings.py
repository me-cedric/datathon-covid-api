# -*-coding:Latin-1 -*

# Extern packages
import numpy
import cv2

class SegmentationSettings :
	path   = "ready_for_segmentation/"
	width  = 512
	height = 512
	format = ".png"
	color  = cv2.IMREAD_GRAYSCALE
	interpolation = cv2.INTER_AREA	

class ClassificationSettings :
	path   = "ready_for_classification/"
	width  = 512
	height = 512
	format = ".png"
	color  = cv2.IMREAD_GRAYSCALE
	interpolation = cv2.INTER_AREA	

