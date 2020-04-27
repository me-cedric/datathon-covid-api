import cv2
import os
import pydicom

def dicomConvert(inputfile, outputdirectory):
    ds = pydicom.read_file(inputfile) # read dicom image
    img = ds.pixel_array # get image array
    out_path = outputdirectory + inputfile.replace('.dcm','.png')
    cv2.imwrite(out_path, img) # write png image
    return out_path