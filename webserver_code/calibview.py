from picamera import PiCamera
import cv2 as cv
from os.path import exists

calibSrc = cv.imread('no_pot.jpg')
calibDsp = calibSrc.copy()
_state = 'running'
_view = [(0, 0), (0, 0)]
_thresh = 127

def DisplayCalib(thresh, p1, p2):
    global calibSrc
    global calibDsp
    (_, calibDsp) = cv.threshold(calibSrc, thresh, 255, cv.THRESH_BINARY)
    calibDsp = cv.rectangle(calibDsp, p1, p2, (0, 0, 255))
    calibDsp = cv.cvtColor(calibDsp, cv.COLOR_GRAY2BGR)
    cv.imshow('calib', calibDsp)

def onChangeThresh(pos):
    global _thresh
    _thresh = pos
    DisplayCalib(_thresh, _view[0], _view[1])

def onSetFrame(event, x, y, flags, blah):
    global _state
    global _thresh
    global _view
    if _state == 'calibrating':
        if event == cv.EVENT_LBUTTONUP:
            _view[0] = (x, y)
            _state = 'croppingEnd'
    elif _state == 'croppingEnd':
        if event == cv.EVENT_LBUTTONUP:
            _view[1] = (x, y)
            DisplayCalib(_thresh, _view[0], _view[1])
            _state = 'calibrating'
        elif event == cv.EVENT_MOUSEMOVE:
            DisplayCalib(_thresh, _view[0], (x, y))

cv.namedWindow('calib')
cv.createTrackbar('threshold', 'calib', _thresh, 255, onChangeThresh)
cv.setMouseCallback('calib', onSetFrame)

def GrayClahe(image):
    lab= cv.cvtColor(image, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv.merge((cl,a,b))
    color = cv.cvtColor(limg, cv.COLOR_LAB2BGR)
    return cv.cvtColor(color, cv.COLOR_BGR2GRAY)

_state = 'calibrating'
PiCamera.capture('/home/pi/calib.jpg')
calibSrc = cv.imread('/home/pi/calib.jpg')
calibSrc = GrayClahe(calibSrc)
DisplayCalib(_thresh, _view[0], _view[1])

cv.waitKey()

if (_view[0][0] > _view[1][0]):
    _view[0], _view[1] = _view[1], _view[0]
if exists('/home/pi/config.txt'):
    f = open('/home/pi/config.txt', 'r')
    lines = f.readlines()
    f.close()
    if (len(lines) < 1):
        lines.append('\n')
else:
    lines = [""]
lines[0] = '{},{},{},{},{}\n'.format(_thresh, _view[0][0], _view[0][1], _view[1][0], _view[1][1])
f = open('/home/pi/config.txt', 'w')
f.writelines(lines)
f.close()