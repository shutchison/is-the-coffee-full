from genericpath import exists
from picamera import PiCamera
import cv2 as cv
import numpy as np
import argparse

thresh = 0
view = [(0,0), (0,0)]
samples = []

def GrayClahe(image):
    lab= cv.cvtColor(image, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv.merge((cl,a,b))
    color = cv.cvtColor(limg, cv.COLOR_LAB2BGR)
    return cv.cvtColor(color, cv.COLOR_BGR2GRAY)

def ReadCalibration():
    global thresh
    global view
    f = open('/home/pi/config.txt', 'r')
    settings =f.readlines()[0].split(',')
    try:
        thresh = int(settings[0])
    except:
        print("Couldn't get threshold from config.")
        exit(0)
    try:
        view[0] = (int(settings[1]), int(settings[2]))
    except:
        print("Couldn't get first view frame corner from config.")
        exit(0)
    try:
        view[1] = (int(settings[3]), int(settings[4]))
    except:
        print("Couldn't get first view frame corner from config.")
        exit(0)
    f.close()

def GetPercent(image):
    total = np.size(image)
    black = total - cv.countNonZero(image)
    return black / total

parser = argparse.ArgumentParser(description='Get a range of values to calibrate the coffee level detection.')
parser.add_argument('--level', help='low or high', default='low',choices=['low','high'])
args = parser.parse_args()

ReadCalibration()
while True:
    k = cv.waitKey()
    
    if k == 32:
        PiCamera.capture('/home/pi/calib.jpg')
        input = cv.imread('/home/pi/calib.jpg')
        input = GrayClahe(input[view[0][1]:view[1][1], view[0][0]:view[1][0]])
        (_, input) = cv.threshold(input, thresh, 255, cv.THRESH_BINARY)
        samples.append(GetPercent(input))
    elif k == 13:
        idx = 1 if args.level == 'low' else 2
        if exists('/home/pi/config.txt'):
            f = open('/home/pi/config.txt', 'r')
            lines = f.readlines()
            f.close()
            while len(lines) < (idx + 1):
                lines.append('\n')
        else:
            lines = ['\n','\n','\n']
        lines[idx] = '{},{}\n'.format(min(samples), max(samples))
        f = open('/home/pi/config.txt', 'w')
        f.writelines(lines)
        f.close()
        break
