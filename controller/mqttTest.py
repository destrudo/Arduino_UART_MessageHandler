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
UMH_00 = UART_MH("/dev/ttyUSB0")

uartNeopixel_00 = UART_Neopixel(UMH_00)
uartConfig_00 = UART_Config(UMH_00)
uartDigital_00 = UART_Digital(UMH_00)

mqttI.add_instance("mhconfig", uartConfig_00, uartConfig_00.device.identityS)
mqttI.add_instance("neopixel", uartNeopixel_00, uartNeopixel_00.device.identityS)
mqttI.add_instance("digital", uartDigital_00, uartDigital_00.device.identityS)

mqttI.run()

print("Done in main.")