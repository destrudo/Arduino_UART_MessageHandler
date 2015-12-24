#!/usr/bin/python

from UARTMessageHandler import *
import pprint
import time

UMH_00 = UART_MH("/dev/ttyUSB0")

CFGI = UART_Config(UMH_00)

print "Manage data: "
pprint.pprint(CFGI.cfg_manage())

#umhInstance = UART_Neopixel("/dev/ttyUSB0")

#umhInstance.np_add(0, 6, 101)

#umhInstance.np_add(1, 5, 4)

#umhInstance.np_clear(0)

#umhInstance.np_clear(1)

#bingo = {}
#counter = 0
#startTime = time.time()
#lastTime = time.time()
#for i in range(0, 100):
#	lastTime = time.time()
#	bingo[str(i)] = [10,0,50]
#	umhInstance.np_set(0, bingo)
#	print("%s objects set, time elapsed: %s, last time: %s" % ( str(i), str(time.time() - startTime), str(time.time() - lastTime) ) )
#	bingo = None
#	bingo = {}

#time.sleep(1)
#umhInstance.np_clear(0)

#umhInstance.np_clear(1)

#umhInstance.np_del(1)
#umhInstance.np_del(0)
