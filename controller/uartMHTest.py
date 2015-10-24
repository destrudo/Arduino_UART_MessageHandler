#!/usr/bin/python

from UARTMessageHandler import *
import pprint

pprint.pprint(lrcsum([ 0, 1, 2 ]))

dicks = UART_Neopixel("/dev/ttyUSB0")

dicks.np_add(0, 6, 101)

bingo = {}
for i in range(99, 101):
	bingo[str(i)] = [100,0,0]

dicks.np_set(0, bingo)