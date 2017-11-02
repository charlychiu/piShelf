import requests
import json
import time
import RPi.GPIO as GPIO

lastLine="" #Init
countLine=0 #Init
fileLocation='../readQr.txt'

#lastLine = fp.readlines()[-1]   
def init():
    with open(fileLocation) as fp:
        d=fp.readlines()
        global countLine
        countLine = len(d)
    fp.closed

def check_QRcatch():
    with open(fileLocation) as fp:
        d=fp.readlines()
        tmp = len(d)
    fp.closed
    with open(fileLocation) as fp:
	global countLine
        if tmp > countLine:
            global lastLine
            #global countLine
            countLine = tmp
            lastLine = fp.readlines()[-1]
            string_handle()
            network_handle()
    fp.closed

def string_handle():
    global lastLine
    lastLine = lastLine.strip()
    lastLine = lastLine.split(':')
    lastLine = lastLine[1]
    print lastLine

def network_handle():
    global lastLine
    r = requests.post('http://120.105.129.146/api/reqShelf', data = {'qrcode_content':lastLine})
    #res = r.json()
    res = r.text
    j = json.loads(res)
    #print(res)
    result = j['result']
    layer = j['layer']
    print result
    print layer
    if result:
        print "openShelf layer :"
        print layer
        if layer == 1:
            control_light(37)
            control_io(22)
            #control_light(37)
        if layer == 2:
            control_light(35)
            control_io(18)
            #control_light(35)
        if layer == 3:
            control_light(33)
            control_io(16)
            #control_light(33)
def gpio_global():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(16, GPIO.OUT)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(16, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    GPIO.output(22, GPIO.LOW)
    GPIO.setup(19, GPIO.IN)
    GPIO.setup(21, GPIO.IN)
    GPIO.setup(23, GPIO.IN)
    GPIO.setup(33, GPIO.OUT)
    GPIO.setup(35, GPIO.OUT)
    GPIO.setup(37, GPIO.OUT)
    GPIO.output(33, GPIO.LOW)
    GPIO.output(35, GPIO.LOW)
    GPIO.output(37, GPIO.LOW)

def control_io(pin):
    GPIO.output(pin, GPIO.HIGH)     ## Turn on GPIO pin (HIGH)
    time.sleep(10)                   ## Wait 1 second
    GPIO.output(pin, GPIO.LOW)      ## Turn off GPIO pin (LOW)
    #GPIO.cleanup()                  ## Cleanup

def control_light(pin):
    GPIO.output(pin, GPIO.HIGH)     ## Turn on GPIO pin (HIGH)
    time.sleep(2)                   ## Wait 1 second
    GPIO.output(pin, GPIO.LOW)      ## Turn off GPIO pin (LOW)
    #GPIO.cleanup() 

def doorState():
    print GPIO.input(19)
    print GPIO.input(21)
    print GPIO.input(23)
    print "---------"

init()
gpio_global()
while True:
    #control_light(33)
    #control_light(35)
    #control_light(37)
    #control_io(16)
    #doorState()
    check_QRcatch()
    time.sleep(3)
