# -*-coding:Latin-1 -*

# Extern packages
import numpy
import cv2
import os
from settings import SegmentationSettings
from settings import ClassificationSettings

def load_image ( path, type ) :
	return cv2.imread ( path, type )
	
def write_image ( img, path ) :
	cv2.imwrite ( path, img )
	print ( "File '%s' has been created" % (path) )
	
def resize_image ( img, width, height, interpolation_type ) :
	return cv2.resize( img, (width, height), interpolation = interpolation_type )
	
def segmentation_standardization ( input_path ) :
	# Create writting path
	basename = os.path.basename ( input_path )
	[ filename, extension ] = os.path.splitext ( basename )
	writting_path = SegmentationSettings.path + filename + SegmentationSettings.format
	
	# Check if file already exists or should be created
	if os.path.isfile ( writting_path ) :
		print ( "File '%s' already exists" % ( writting_path ) )
	else :
		img = load_image ( input_path, SegmentationSettings.color )
		img = resize_image ( img, SegmentationSettings.width, SegmentationSettings.height, SegmentationSettings.interpolation )
		write_image ( img, writting_path )
		
	return writting_path
	
def display_image ( img, path ) :
	[ m, n ] = img.shape
	caption = "%s [ %s x %s ]" % (path, m, n)
	cv2.imshow( caption, img )
	cv2.waitKey ( 0 )
	
# Test function
path = "input_images/scan.jpg"
seg_path = segmentation_standardization ( path )
seg_img = load_image ( seg_path, SegmentationSettings.color )
display_image ( seg_img, seg_path )

# Closing app
os.system ( "pause" )
cv2.destroyAllWindows ( )

