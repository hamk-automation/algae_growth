import time, math
import RPi.GPIO as GPIO
import numpy
import max31865
import json
misoPin = 21
mosiPin = 19
clkPin  = 23
def measure_temperature(csPin = 24):

   ##Set up class of each sensor
	max       = max31865.max31865(csPin,misoPin,mosiPin,clkPin)

   ##Calculate and read those sensors
	tempC     = max.readTemp()
	while tempC < -200 or tempC > 200:
		tempC = max.readTemp()
	# jsonData  = {"temperature(pin {})".format(csPin):tempC}
	return tempC
	#GPIO.cleanup()
# while True:
# 	print(measure_temperature(24))
# 	print(measure_temperature(26))
# 	time.sleep(3)
