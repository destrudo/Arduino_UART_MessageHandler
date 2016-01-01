#!/usr/bin/python

from UARTMessageHandler import *
import pprint
import time
import binascii

UMH_00 = UART_MH("/dev/ttyUSB0")

CFGI = UART_Config(UMH_00)
umhInstance = UART_Neopixel(UMH_00)

mgmtO = CFGI.cfg_manage()

print "Manage data: "
pprint.pprint(mgmtO)

umhInstance.np_add(0, 6, 101)

#umhInstance.np_add(1, 5, 4)

umhInstance.np_clear(0)

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


tmpData = {
	"start":0,
	"end":100,
	"startColor":[ 255, 255, 0 ],
	"endColor":[ 255, 0, 255 ],
}
umhInstance.np_gradient(0, tmpData)

time.sleep(4)
umhInstance.np_clear(0)

#umhInstance.np_clear(1)

#umhInstance.np_del(1)
#umhInstance.np_del(0)
