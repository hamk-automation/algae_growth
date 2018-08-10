#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from tsl2561 import  TSL2561
import RPi.GPIO as GPIO
import json
import time

'''Driver for the TSL2561 digital luminosity (light) sensors.
Pick one up at http://www.adafruit.com/products/439
Adafruit invests time and resources providing this open source code,
please support Adafruit and open-source hardware by purchasing
products from Adafruit!
Code ported from Adafruit Arduino library,
commit ced9f731da5095988cd66158562c2fde659e0510:
https://github.com/adafruit/Adafruit_TSL2561
'''
# link to github code: https://github.com/sim0nx/tsl2561
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
#Set GPIO pin 29 is the Addr pin of second sensor
GPIO.setup(29, GPIO.OUT)
#Set pin 29 to high, so that the address of  second sensor will change from default(0x39) to 0x49
GPIO.output(29, GPIO.HIGH)
def measure_lux(address):
                tsl =TSL2561(debug=True,address=address)
                tsl.set_auto_range(True)
                if address == 0x39 or 0x49:
                    # jsonData = {"lux({})".format(address):tsl.lux()}
                    return tsl.lux()


                    ##Uncomment if you want to load infrared broadband information
                    # broadband,ir=tsl._get_data()
                    # print(broadband)
                    # print(ir)
                else:
                    print("doesnt exist that sensor")

#Uncomment to test

#testLux()
