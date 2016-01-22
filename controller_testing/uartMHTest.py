#!/usr/bin/python

from UARTMessageHandler import *
import pprint
import sys
import time
import binascii

UMH_00 = UART_MH("/dev/ttyUSB0")

CFGI = UART_Config(UMH_00)
umhNPInstance = UART_Neopixel(UMH_00)
umhInstance = UART_Digital(UMH_00)
mgmtO = CFGI.cfg_manage()

print "Manage data: "
pprint.pprint(mgmtO)

# print "Running NP get"
# pprint.pprint(umhNPInstance.np_get(0,{ "id":0 }))

print "Running NP add"
umhNPInstance.np_add(0,3,100)

# print "Running NP get 2"
# pprint.pprint(umhNPInstance.np_get(0,{ "id":0 }))
while (True):
	print "Setting gradient."
	umhNPInstance.np_gradient(0, { "start":0, "end":100, "startColor":[255,100,0], "endColor":[0,100,100] })

	print "Running NP get 3"
	pprint.pprint(umhNPInstance.np_get(0,{ "id":0 }))

	print "Clearing."
	umhNPInstance.np_clear(0)

	time.sleep(1)


#while (True):
#	umhNPInstance.np_gradient(0, { "start":0, "end":100, "startColor":[255,100,0], "endColor":[0,100,100] })
#	umhNPInstance.np_clear(0)


# #print "Digital test 00:"
# rawO = umhInstance.createMessage( { "data":[], "command":"manage" } )
# pprint.pprint(rawO)

# print "Digital test 01:"
# raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":8, "dir":1, "class":0 }, "command":"add" } ))
# pprint.pprint(raw1)

# print "Digital test 02:"
# raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":7, "dir":0, "class":0 }, "command":"add" } ))
# pprint.pprint(raw1)

# print "Digital test 03:"
# raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":5, "dir":1, "class":1 }, "command":"add" } ))
# pprint.pprint(raw1)

# print "Performing first pin mode change, setting to input."
# raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":5, "dir":1, "class":1 }, "command":"cpin" } ))
# pprint.pprint(raw1)

# print "Digital test 04:"
# raw2 = umhInstance.createMessage( { "data":[], "command":"manage" } )
# pprint.pprint(raw2)


# print "Digital test 05:"
# raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":7}, "command":"get" } ))
# pprint.pprint(raw1)

# print "Performing analog test:"
# for i in range(0, 255):
# 	raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":5, "value":i }, "command":"set" } ))
# 	#if int(raw1):
# 	#	print "Err in loop."

# raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":5, "value":100 }, "command":"set" } ))
# pprint.pprint(raw1)

# time.sleep(1)

# # print "Performing last pin mode change, setting to input."
# # raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":5, "dir":0, "class":0 }, "command":"cpin" } ))
# # pprint.pprint(raw1)

# # time.sleep(1)

# # print "Deleting pin 7"
# # raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":7 }, "command":"del" } ))
# # pprint.pprint(raw1)

# time.sleep(1)

# # print "Performing pin mode change, setting to output."
# # raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":5, "dir":1, "class":0 }, "command":"cpin" } ))
# # pprint.pprint(raw1)


# sys.exit(1)
# for i in range(0, 100):
# 	print "Digital test 03:"
# 	raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":8, "value":0 }, "command":"set" } ))
# 	pprint.pprint(raw1)

# 	time.sleep(1)

# 	print "Digital test 04:"
# 	raw1 = umhInstance.device.sendMessage(umhInstance.createMessage( { "data":{ "pin":8, "value":1 }, "command":"set" } ))
# 	pprint.pprint(raw1)

# 	time.sleep(2)

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


#tmpData = {
#	"start":0,
#	"end":100,
#	"startColor":[ 255, 255, 0 ],
#	"endColor":[ 255, 0, 255 ],
#}
#umhInstance.np_gradient(0, tmpData)

#time.sleep(4)
#umhInstance.np_clear(0)

#umhInstance.np_clear(1)

#umhInstance.np_del(1)
#umhInstance.np_del(0)
