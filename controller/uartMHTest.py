#!/usr/bin/python

from UARTMessageHandler import *
import pprint
import time

umhInstance = UART_Neopixel("/dev/ttyUSB0")

umhInstance.np_add(0, 6, 101)
umhInstance.np_add(1, 5, 4)

umhInstance.np_clear(0)
umhInstance.np_clear(1)

bingo = {}
counter = 0
for i in range(0, 4):
	print("i = %s" % (str(i)))
	bingo[str(i)] = [0,0,255]
	umhInstance.np_set(0, bingo)
	bingo = None
	bingo = {}

umhInstance.np_set(1, {"1":[100,100,100]})
time.sleep(1)

umhInstance.np_clear(1)
umhInstance.np_clear(0)

umhInstance.np_del(1)
umhInstance.np_del(0)
