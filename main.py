from time            import sleep
from multiprocessing import Process
import threading
import RPi.GPIO as GPIO
import sys
import json
from socketIO_client_nexus import SocketIO
import timeit
GPIO.cleanup()
from lux        import measure_lux
from PH_library import measure_PH,AtlasI2C
from pt100      import measure_temperature

mutex =threading.Lock() # add lock for 2 threads to avoid critical section
def read():
    while True:
        sleep(4)
        mutex.acquire() #Lock thread when reading
        try:
            measurement = float(measure_PH()) # PH_value measured
        except ValueError:
            measurement = "Cannot read while calibrating"
        mutex.release() #Remove lock
        jsonData={"lux(0x39)":measure_lux(0x39),
                  "lux(0x49)":measure_lux(0x49),
                  "current_PH_value":measurement,
                  "temperature(pin 24)":measure_temperature(24),
                  "temperature(pin 26)":measure_temperature(26)};
        newjson=json.dumps(jsonData, sort_keys=True);
        print(newjson)
        sleep(4)
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
    while True: #keep the thread alive to continue listening
        pass
print("Press Ctrl-Z to kill all threads. Ctrl-C is only focus by main thread")
#Use multithreading to read and listen to calibrating event at the same time
read_thread      =threading.Thread(name="read"     ,target=read)
calibrate_thread =threading.Thread(name="calibrate",target=calibrate_PH)
try:
    read_thread.start()
    calibrate_thread.start()

except KeyboardInterrupt:
    print("end program")
    sys.exit(1)
