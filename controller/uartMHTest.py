#!/usr/bin/python

from UARTMessageHandler import *
import pprint

pprint.pprint(lrcsum([ 0, 1, 2 ]))

dicks = UART_Neopixel("/dev/ttyUSB0")

dicks.np_add(0, 6, 101)

dicks.np_clear(0)

bingo = {}
counter = 0
for i in range(0, 10):
#	print("i = %s, j = %s" % (str(i), str(j)))
	bingo[str(i)] = [0,0,255]
	dicks.np_set(0, bingo)
	bingo = None
	bingo = {}

dicks.np_clear(0)

dicks.np_del(0)