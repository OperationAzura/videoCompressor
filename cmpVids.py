import subprocess
import os
import numpy as numpy
import cv2
import pytesseract
import sys
import time
import logging

#set logging config
logging.basicConfig(level=logging.DEBUG, filename='/home/pi/Pictures/encode.log', filemode='a')

#encoder to use - libx265 is very slow, but best quality, h264xxx 100x faster but poor quality and errors
ENCODER = 'libx265'  #'h264_omx' #h265_v4l2m2m'

#compression factor
CRF = '28'

#path to ffmpeg binary
FFMPEG_PATH = '/home/pi/FFmpeg/ffmpeg'

#Number of threads to use
THREADCOUNT = '4'

#COUNT
count = 0

#CompressVideos will read in all the video fiels, compress them using ffmpeg and rename them based on OCR'd image data
def CompressVideos():
    global count
    paths = ['/home/pi/Pictures/CarPort/',
    '/home/pi/Pictures/FrontDoor/']
    
    for p in paths:
        # get a list of files
        fList = filter(lambda f: f.split('.')[-1] == 'mp4', os.listdir(p))

        # encode each file
        for fName in fList:
            count = count + 1
            Encode(p, fName)

#Encode taqkes a file name then loads and encodes using ffmpeg
def Encode(path, fName):
    #Get the camera name based on the Dir
    camName = path.split('/')[-2]
    #Put name in better format
    name = fName[2:].split('.')[0]
    name = '_'.join([name[:5], name[5:7], name[7:9], name[9:]])
    name = ''.join([camName , name])

    output = '/home/pi/Pictures/cmpVids/{}.mp4'.format(name)

    try:
        command = [
            FFMPEG_PATH, '-i', path + fName,
            '-c:v', ENCODER , '-crf', CRF,
        ]

        command += ['-threads', THREADCOUNT,'-flags', '+global_header', '-an', output]    # add threads and output
        exitStatus = subprocess.call(command)                # encode the video!
        logging.info('Encoding file: ' + path + fName)
        logging.info('ExitStatus: ' + str(exitStatus))
        logging.info('Output file: ' + output)

        if exitStatus == 0:
            os.remove(path + fName)
            os.remove(path + fName.split('.')[0] + '.jpg')
            logging.info('Success, output file removed')
        else:
            logging.warning('Something failed, file not removed, exitStatus: ' + exitStatus)
            
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
            logging.warning(e.message)
        else:
            print(e)
            logging.warning(e)

if __name__ == "__main__":
    start = time.perf_counter()
    CompressVideos()
    print('count: ', count)
    logging.info('count: ' + str(count))
    print('duration: ', (time.perf_counter() - start))
    logging.info('duration: ' + str(time.perf_counter() - start))
