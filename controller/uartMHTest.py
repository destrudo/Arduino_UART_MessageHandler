#!/usr/bin/python

from UARTMessageHandler import *
import pprint

dicks = UART_Neopixel("/dev/ttyUSB0")

dicks.np_add(0, 6, 101)

print("MANAGE:")
pprint.pprint(dicks.np_manage())
print("MANAGE END:")

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