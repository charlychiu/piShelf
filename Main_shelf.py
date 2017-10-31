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
    print result
    if result:
        layer = j['layer']
        print "openShelf layer :"
        print layer
        control_io(7)

def control_io(pin):
    GPIO.setmode(GPIO.BOARD)
    #GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)     ## Turn on GPIO pin (HIGH)
    time.sleep(1)                   ## Wait 1 second
    GPIO.output(pin, GPIO.LOW)      ## Turn off GPIO pin (LOW)
    time.sleep(1)                   ## Wait 1 second
    GPIO.cleanup()                  ## Cleanup
    

init()
while True:
    #control_io(7)
    check_QRcatch()
    time.sleep(5)
