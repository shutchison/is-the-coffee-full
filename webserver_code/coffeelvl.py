import math
import cv2 as cv
import numpy as np
import MySQLdb as mysql
import os
from twilio.rest import Client
from os.path import exists
import time

thresh = 0
view = [(0,0), (0,0)]
range = [(0,0.1), (0.9,1)]

def ReadConfig():
    global thresh
    global view
    global range
    f = open('config.txt', "r")#/home/pi/config.txt', 'r')
    lines = f.readlines()
    f.close()
    if len(lines) < 3:
        print('Config too short.')
        exit(0)
    settings = lines[0].split(',')
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
    settings = lines[1].split(',');
    try:
        range[0] = (float(settings[0]), float(settings[1]))
    except:
        print("Couldn't get lower level range from config.")
        exit(0)
    settings = lines[2].split(',');
    try:
        range[1] = (float(settings[0]), float(settings[1]))
    except:
        print("Couldn't get upper level range from config.")
        exit(0)

def Cvt2Ref(image):
    global view
    global thresh
    framed = image[view[0][1]:view[1][1], view[0][0]:view[1][0]]
    lab= cv.cvtColor(framed, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv.merge((cl,a,b))
    color = cv.cvtColor(limg, cv.COLOR_LAB2BGR)
    grayclaw = cv.cvtColor(color, cv.COLOR_BGR2GRAY)
    (_, final) = cv.threshold(grayclaw, thresh, 255, cv.THRESH_BINARY)
    return final

def GetPercent(image):
    total = np.size(image)
    black = total - cv.countNonZero(image)
    return black / total

def GetCoffeeLevel():
    IP = "localhost"
    u = "plotRequester"
    p = "AntSJ_Dorito"
    database_name = "coffeepotHistory"
    table_name = "coffeeHistory"
    port = 3306
    ReadConfig()
    
    input = Cvt2Ref(cv.imread("/var/www/html/image.jpg"))#./home/pi/image.jpg'))
    percent = GetPercent(input)
    step = min(range[0][1]-range[0][0], range[1][1]-range[1][0])
    full_range = range[1][0] - range[0][1]
    levels = math.floor(full_range / step)
    step = full_range / levels
    db = mysql.connect(host=IP,port=port,user=u,passwd=p,db=database_name)
    cursor = db.cursor()
    if range[0][0] > percent or percent > range[1][1]:
    #    print(-1)
        estimate = -1
    elif range[0][0] <= percent and percent <= range[0][1]:
    #    print(0)
        estimate = -1
    elif range[1][0] <= percent and percent <= range[1][1]:
    #    print(1)
        estimate = 1
    else:
        estimate = ((percent - range[0][1]) / step) / levels
    #    print(estimate)
    print(estimate)
    if estimate != -1:
        print("INSERT INTO {} (time, potLevel) VALUES (\'{}\', {});".format(table_name, time.strftime('%Y-%m-%d %H:%M:%S'), estimate))
        cursor.execute("INSERT INTO {} (time, potLevel) VALUES (\'{}\', {});".format(table_name, time.strftime('%Y-%m-%d %H:%M:%S'), estimate))    
        db.commit()
    
    cups = round(estimate * 5)
    if cups >= 0:
        if exists('system_vars.txt'):
            f = open('system_vars.txt', 'r')
            hasSent = int(f.read()) > 0
            f.close()
        else:
            hasSent = False
        
        if cups == 0:
            result = 'Needs refill'
            if not hasSent:
                account_sid = os.environ['TWILIO_ACCOUNT_SID']
                auth_token = os.environ['TWILIO_AUTH_TOKEN']
                client = Client(account_sid, auth_token)

                message = client.messages \
                .create(
                     body="Coffee pot needs to be refilled!",
                     from_='+19127859923',
                     to='+17135042933'
                )
                print(message.sid)
                hasSent = True
        elif cups == 1:
            result = 'About 1 cup left'
            hasSent = False
        else:
            result = 'About {} cups left'.format(cups)
            hasSent = False
        
        img = np.zeros((35,300,4), dtype=np.uint8)
        cv.putText(img, result, (4, 26), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255, 255), 2, cv.LINE_4)
        cv.imwrite('/var/www/html/cups.png',img)
        
        f = open('system_vars.txt', 'w')
        f.write('{}'.format(1 if hasSent else 0))
        f.close()
