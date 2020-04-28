import cv2
import os
import pydicom
from pathlib import Path

def dicomConvert(inputfile, outputdirectory):
    ds = pydicom.read_file(inputfile) # read dicom image
    img = ds.pixel_array # get image array
    out_path = Path(outputdirectory).resolve() / Path(inputfile).name.replace('.dcm','.png')
    out_path.touch()
    cv2.imwrite(str(out_path), img) # write png image
    return str(out_path)