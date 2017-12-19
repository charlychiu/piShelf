# coding: utf-8
import sys, os, time, signal
reload(sys)
sys.setdefaultencoding('utf-8')
import threading
import paho.mqtt.client as mqtt
import requests
import json
import RPi.GPIO as GPIO

lastLine="" #Init
countLine=0 #Init
fileLocation='../readQr.txt'


client = None
mqtt_looping = False
reading_thread = None

TOPIC_ROOT = "shelf"

def on_connect(mq, userdata, rc, _):
    # subscribe when connected.
    mq.subscribe(TOPIC_ROOT + '/#')

def on_message(mq, userdata, msg):
    print "topic: %s" % msg.topic
    print "payload: %s" % msg.payload
    print "qos: %d" % msg.qos
	if msg.payload == "1":
		control_light(37)
        control_io(22)
	if msg.payload == "2":
		control_light(35)
        control_io(18)
	if msg.payload == "3":
		control_light(33)
        control_io(16)

def status_reading():
    while True:
        #status = gate.read()
        time.sleep(1)   # 假設讀取狀態
        status = "noop"

        if mqtt_looping:
            check_QRcatch()
			time.sleep(3)
        else:
            print "quit status reading thread"
            return

def mqtt_client_thread():
    global client, mqtt_looping
    client_id = "" # If broker asks client ID.
    client = mqtt.Client(client_id=client_id)

    # If broker asks user/password.
    user = ""
    password = ""
    client.username_pw_set(user, password)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect("120.105.129.137")
    except:
        print "MQTT Broker is not online. Connect later."

    mqtt_looping = True
    print "Looping..."

	reading_thread = threading.Thread(target=status_reading)
    reading_thread.start()
	
    #mqtt_loop.loop_forever()
    cnt = 0
    while mqtt_looping:
        client.loop()

        cnt += 1
        if cnt > 20:
            try:
                client.reconnect() # to avoid 'Broken pipe' error.
            except:
                time.sleep(1)
            cnt = 0

    print "quit mqtt thread"
    client.disconnect()

def stop_all(*args):
    global mqtt_looping
    mqtt_looping = False
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
	
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, stop_all)
    signal.signal(signal.SIGQUIT, stop_all)
    signal.signal(signal.SIGINT,  stop_all)  # Ctrl-C
	init()
	gpio_global()
    mqtt_client_thread()
	reading_thread.join()

    print "exit program"
    sys.exit(0)