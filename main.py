from time            import sleep
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
from max31865           import measure_temperature
from Adafruit_ADS1x15   import ADS1015


devices = AtlasI2C() #PH_sensor instance
adc     = ADS1015()  #PAR_sensor instance
adc.start_adc(0, gain = 2)
mutex   = threading.Lock() # add lock for 2 threads to avoid critical section
def read():
    """ This function reads, prints and sends measurement values to the database.
    """
    while True:
        # Measure Lux_ under water
        try:
            lux1_value  = measure_lux(0x39)
        except:
            lux1_value  = -1
            print("TSL2561_1 crashes")

        # Measure Lux_ above water level
        try:
            lux2_value  = measure_lux(0x49)
        except:
            lux2_value = -1
            print("TSL2561_2 crashes")

        # Measure Temperature_ under water
        try:
            temp1_value = measure_temperature(24)
        except:
            temp1_value = -1
            print("MAX31865_1 crashes")

        # Measure Temperature_ above water level and sensor calibration to same
        try:
            temp2_value = measure_temperature(26)
        except:
            temp2_value = -1
            print("MAX31865_2 crashes")

        # Measure PAR_value
        try:
            PAR_value   = adc.get_last_result()*0.8
        except:
            PAR_value   = -1
            print("PAR_sensor crashes")

        #Measure PH_value after temperature calibration
        mutex.acquire() #Lock thread when reading
        try:
            if temp1_value >-200 and temp1_value<200 and temp1_value != -1:
                tempCaliCommand = "T," + str(temp1_value)
                devices.query(tempCaliCommand)
            else:
                print("Measure PH without temp calibration")
            measurement_PH = float(devices.query("R")) # Read PH_value
        except :
            measurement_PH = -1
            print("PH_sensor crashes")
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
        sleep(5)

def calibrate_PH():
    """
    This function creates a client endpoint in socket connection between nodeJS
    and python process, listens continuosly to socketIO event, calibrates PH-circuit
    with received information.
    If calibration succeed, send back a success message.
    Else, send back an error message.
    """
    devices    = AtlasI2C();
    socket_url = "localhost"

    socketIO = SocketIO(socket_url, 9000, verify=False)
    def start_calibrate(*arg):
        try:
            print(arg)
            a  = arg[0][u'data']
            print(a)
            commandList = { "low": "cal,low,4", "medium": "cal,mid,7","high":"cal,high,10"}
            command = commandList.get(a)
            print(command)
            mutex.acquire()
            devices.query(command)
            sleep(0.1)
            status = devices.query('cal,?')
            status = status[-1]
            socketIO.emit('success',status)
            f = open("Server/status.txt","w+")
            f.write(status)
            f.close()
            print("Command Successful")
            mutex.release()
        except :
            socketIO.emit("error")
            print("Wrong Command")
    socketIO.on('send_data',start_calibrate) #Listen to calibrating event
    socketIO.wait()
    while True: #keep the thread alive to continue listening to socket event
        pass
print("Press Ctrl-Z to kill all threads. Ctrl-C is only noticed by main thread")
#Use multithreading to read and listen to calibrating event at the same time
read_thread      =threading.Thread(name="read"     ,target=read)
calibrate_thread =threading.Thread(name="calibrate",target=calibrate_PH)

read_thread.start()
calibrate_thread.start()
