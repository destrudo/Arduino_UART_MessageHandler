#!/usr/bin/python

###############################################################################
#                                  mqttTest.py                                #
#                                                                             #
# This is a sample application implementation for UART_MH_MQTT.               #
#                                                                             #
# Copyright(C) 2015, Destrudo Dole                                            #
#                                                                             #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation, version 2 of the license.                              #
###############################################################################

from UARTMessageHandler import *
import pprint
import time

mqttI = UART_MH_MQTT("127.0.0.1",1883)
uartNeopixelI = UART_Neopixel("/dev/ttyUSB0")

mqttI.add_instance("neopixel", uartNeopixelI)
mqttI.run()