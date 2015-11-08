#!/usr/bin/python

from UARTMessageHandler import *
import pprint
import time

dicks = UART_Neopixel("/dev/ttyUSB0")

dicks.np_add(0, 6, 101)
dicks.np_add(1, 5, 4)

print("MANAGE:")
pprint.pprint(dicks.np_manage())
print("MANAGE END:")

dicks.np_clear(0)
dicks.np_clear(1)

bingo = {}
counter = 0
for i in range(0, 4):
	print("i = %s" % (str(i)))
	bingo[str(i)] = [0,0,255]
	dicks.np_set(0, bingo)
	bingo = None
	bingo = {}

dicks.np_set(1, {"1":[100,100,100]})
time.sleep(1)

dicks.np_clear(1)
dicks.np_clear(0)

dicks.np_del(1)
dicks.np_del(0)
