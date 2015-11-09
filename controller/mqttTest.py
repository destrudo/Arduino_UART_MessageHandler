#!/usr/bin/python

from UARTMessageHandler import *
import pprint
import time

mqttI = UART_MH_MQTT("127.0.0.1",1883)

mqttI.run()