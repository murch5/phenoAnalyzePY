# Function for extracting individual frame from directory of TIFF files

import matplotlib.pyplot as plt
import numpy as np

def extractSingleChannel(TIFFdata, channel=1):  # TIFFdata - NumPy array of raw TIFF data

    flat = TIFFdata[:, :, channel]  # extract only single channel
    return flat  # return flattened data

def generateFrameFromTIFF(filePath):  # filePath - path of individual image file to load

    image = plt.imread(filePath)  # load TIFF file using matplotlib (with Pillow dependency)
    return image

def loadTIF(fileName):

    image = extractSingleChannel(generateFrameFromTIFF(fileName))
    return image.T

def generateFrameSet(fileList):  # filePath - path of file directory containing TIFF files to load

    #print("TOP:    Loading script: generateFrameSet")
    #print("LOG:    Start Frame Set Generation")
    frames = []
    fileList = fileList
    #print("LOG:       File list contains: " + str(len(fileList)) + " images")
    for file in fileList:
        #print("LOG:    Load image name: " + file)
        frameInt = extractSingleChannel(generateFrameFromTIFF(file))
        frames.append(frameInt.T)
   # print("LOG:    Returning frames")

    return frames  # return list of frames
