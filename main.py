from time            import sleep
from multiprocessing import Process
import threading
import RPi.GPIO as GPIO
import sys
import json
import paho.mqtt.publish as publish
from socketIO_client_nexus import SocketIO
import timeit
GPIO.cleanup()

from lux                import measure_lux
from PH_library         import AtlasI2C
from pt100              import measure_temperature
from Adafruit_ADS1x15   import ADS1015

devices = AtlasI2C() #PH_sensor instance
adc     = ADS1015()  #PAR_sensor instance
adc.start_adc(0, gain = 2)
mutex   = threading.Lock() # add lock for 2 threads to avoid critical section
def read():
    while True:
        try:
            lux1_value  = measure_lux(0x39)
            lux2_value  = measure_lux(0x49)
            temp1_value = measure_temperature(24)
            temp2_value = measure_temperature(26)
            PAR_value   = adc.get_last_result()*0.8
            tempCaliCommand = "T," + str(temp1_value)
            try:
                print(tempCaliCommand)
                mutex.acquire() #Lock thread when calibration
                #devices.query(tempCaliCommand)
                mutex.release() #Remove thread
                sleep(1)
            except ValueError:
                print("Wrong Temperature Calibration Command")
            mutex.acquire() #Lock thread when reading
            try:
                measurement_PH = float(devices.query("R")) # Read PH_value
            except ValueError:
                measurement = "Cannot read while calibrating"
            mutex.release() #Remove lock
            jsonData={"lux1":lux1_value,
                      "lux2":lux2_value,
                      "ph":measurement_PH,
                      "t1":temp1_value,
                      "t2":temp2_value,
                      "par":PAR_value,
		              "location":"Karanoja"};
            newjson=json.dumps(jsonData, sort_keys=True);
            publish.single("alykkaatpalvelut/tu_algae", newjson, hostname="hamkkontti.ddns.net")
            publish.single("alykkaatpalvelut/tu_algae", newjson, hostname="iot.research.hamk.fi")
            print(newjson)
            sleep(9)
        except :
            print("it over")
            GPIO.cleanup()

def calibrate_PH():
    devices    = AtlasI2C();
    socket_url = "localhost"

    socketIO = SocketIO(socket_url, 9000, verify=False)
    def start_calibrate(*arg):
        try:
            print("should be something")
            print(arg)
            a  = arg[0][u'data']
            print(a)
            commandList = { "low": "cal,low,4", "medium": "cal,mid,7","high":"cal,high,10"}
            command = commandList.get(a)
            print(command)
            mutex.acquire()
            tempCaliCommand = "T," + str(measure_temperature(24))
            devices.query(tempCaliCommand)
            devices.query(command)
            print("Command Successful")
            mutex.release()
            socketIO.emit('success')
        except :
            socketIO.emit("error")
            print("Wrong Command")
    socketIO.on('welcome',start_calibrate) #Listen to calibrating event
    socketIO.wait()
    while True: #keep the thread alive to continue listening to socket event
        pass
print("Press Ctrl-Z to kill all threads. Ctrl-C is only noticed by main thread")
#Use multithreading to read and listen to calibrating event at the same time
read_thread      =threading.Thread(name="read"     ,target=read)
calibrate_thread =threading.Thread(name="calibrate",target=calibrate_PH)

read_thread.start()
calibrate_thread.start()
