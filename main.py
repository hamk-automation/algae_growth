from time            import sleep
import threading
import RPi.GPIO as GPIO
import sys
import json
import paho.mqtt.publish as publish
from socketIO_client_nexus import SocketIO
import timeit
import logging
GPIO.cleanup()

from lux                import measure_lux
from PH_library         import AtlasI2C
from max31865           import measure_temperature
from Adafruit_ADS1x15   import ADS1015

#config log
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('/home/pi/Public/main/component.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
#config component
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
            lux1_value,ilux1_value  = measure_lux(0x29)
            vlux1_value             = lux1_value - ilux1_value

        except:
            lux1_value,ilux1_value,vlux1_value  = None,None,None
            logger.warning("TSL2561_1 crashes")

        # Measure Lux_ above water level
        try:
            lux2_value,ilux2_value  = measure_lux(0x49)
            vlux2_value             = lux2_value - ilux2_value
        except:
            lux2_value,ilux2_value,vlux2_value  = None,None,None
            logger.warning("TSL2561_2 crashes")

        # Measure Temperature_ under water
        try:
            temp1_value = measure_temperature(24)
            if temp1_value == None:
                logger.warning("MAX31865_1 gives false value")
        except:
            temp1_value = None
            logger.warning("MAX31865_1 crashes")


        # Measure PAR_value
        try:
            PAR_value   = adc.get_last_result()*0.8
        except:
            PAR_value   = None
            logger.warning("PAR_sensor crashes")


        mutex.acquire() #Lock thread when reading
        # Measure Temperature_ above water level
        try:
            temp2_value = measure_temperature(26)
            if temp2_value == None:
                logger.warning("MAX31865_2 gives false value")
        except:
            temp2_value = None
            logger.warning("MAX31865_2 crashes")
        #Measure PH_value after temperature calibration
        try:
            if temp1_value  != None:
                tempCaliCommand = "T," + str(temp1_value)
                devices.query(tempCaliCommand)
                sleep(0.3)
            else:
                logger.info("Measure PH without temp calibration")
            measurement_PH = float(devices.query("R")) # Read PH_value
        except :
            measurement_PH = None
            logger.warning("PH_sensor crashes")
        mutex.release() #Remove lock
        jsonData={"lux1":lux1_value,
                  "ilux1":ilux1_value,
                  "vlux1":vlux1_value,
                  "lux2":lux2_value,
                  "ilux2":ilux2_value,
                  "vlux2":vlux2_value,
                  "ph":measurement_PH,
                  "t1":temp1_value,
                  "t2":temp2_value,
                  "par":PAR_value,
	              "location":"Karanoja"};
        newjson=json.dumps(jsonData, sort_keys=True);
        #publish.single("alykkaatpalvelut/tu_algae", newjson, hostname="hamkkontti.ddns.net")
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
            logger.info(command)
            mutex.acquire()
            tempRecalibration = "T,"+str(measure_temperature(26))
            devices.query(tempRecalibration)
            sleep(0.3)
            devices.query(command)
            sleep(0.3)
            status = devices.query('cal,?')
            status = status[-1]
            socketIO.emit('success',status)
            f = open("/home/pi/Public/main/Server/status.txt","w+")
            f.write(status)
            f.close()
            logger.info("Calibration Command Successful,"+str(a))
            mutex.release()
        except :
            socketIO.emit("error")
            logger.debug("Wrong Command")
    socketIO.on('send_data',start_calibrate) #Listen to calibrating event
    socketIO.wait()
    while True: #keep the thread alive to continue listening to socket event
        pass
logger.info("Start measuring")
#Use multithreading to read and listen to calibrating event at the same time
read_thread      =threading.Thread(name="read"     ,target=read)
calibrate_thread =threading.Thread(name="calibrate",target=calibrate_PH)

read_thread.start()
calibrate_thread.start()
