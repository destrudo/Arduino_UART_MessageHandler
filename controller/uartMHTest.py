#!/usr/bin/python

from UARTMessageHandler import *
import pprint

pprint.pprint(lrcsum([ 0, 1, 2 ]))

dicks = UART_Neopixel("/dev/ttyUSB0")

#dicks.np_add(0, 6, 101)
dicks.np_set(1, { "2":[255,255,255], "1":[255,0,255] })