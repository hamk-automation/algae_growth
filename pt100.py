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
	return tempC
	#Must remove GPIO.cleanup() because It can affect address of 2 lux sensors
	#GPIO.cleanup()
