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

from lux        import measure_lux
from PH_library import AtlasI2C
from pt100      import measure_temperature

devices = AtlasI2C() #PH_sensor instance
mutex =threading.Lock() # add lock for 2 threads to avoid critical section
def read():
    while True:
        lux1_value  = measure_lux(0x39)
        lux2_value  = measure_lux(0x49)
        temp1_value = measure_temperature(24)
        temp2_value = measure_temperature(26)
        tempCaliCommand = "T," + str(temp1_value)
        try:
            print(tempCaliCommand)
            mutex.acquire() #Lock thread when calibration
            devices.query(tempCaliCommand)
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
                  "t2":temp2_value};
        newjson=json.dumps(jsonData, sort_keys=True);
        publish.single("alykkaatpalvelut/tu_algae", newjson, hostname="hamkkontti.ddns.net")
        print(newjson)
        sleep(9)
def calibrate_PH():
    print("hey")
    devices    = AtlasI2C();
    socket_url = "localhost"

    socketIO = SocketIO(socket_url, 9000, verify=False)
    def start_calibrate(*arg):
        try:
            print("should be something")
            print(arg)
            a  = arg[0][u'data']
            print(a)
            if(a=="low"):
                command = "cal,low,4"
            if(a=="medium"):
                command = "cal,mid,7"
            if(a=="high"):
                command = "cal,high,10"
            print(command)
            mutex.acquire()
            devices.query(command)
            print("Command Successful")
            mutex.release()


        except ValueError:
            print("Wrong Command")
    socketIO.on('welcome',start_calibrate) #Listen to calibrating event
    socketIO.wait()
    while True: #keep the thread alive to continue listening to socket event
        pass
print("Press Ctrl-Z to kill all threads. Ctrl-C is only noticed by main thread")
#Use multithreading to read and listen to calibrating event at the same time
read_thread      =threading.Thread(name="read"     ,target=read)
calibrate_thread =threading.Thread(name="calibrate",target=calibrate_PH)
try:
    read_thread.start()
    calibrate_thread.start()

except KeyboardInterrupt:
    print("end program")
    sys.exit(1)
