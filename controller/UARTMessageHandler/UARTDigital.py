###############################################################################
#                               UARTDigital.py                                #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#                                                                             #
# This is the Digital library which handles all of the digital IO control.    #
#                                                                             #
# Copyright(C) 2015, Destrudo Dole                                            #
#                                                                             #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation, version 2 of the license.                              #
###############################################################################

from __future__ import print_function

import serial
import pprint
import sys
import struct
import time
import socket

from UARTMessageHandler import *
from UARTMessageHandler import isInt
from UARTMessageHandler import to_bytes
from UARTMessageHandler import listOverlay
from UARTMessageHandler import UART_MH

DEBUG = 0

#Arduino state definitions
OUTPUT = 1
INPUT = 0
HIGH = 1
LOW = 0
C_DIGITAL = 0
C_ANALOG = 1


class PinInfo:
	def __init__(self, _pin, _mode, _state, _type):
		self.pin = _pin
		self.mode = _mode
		self.state = _state
		self.type = _type

class UART_Digital:
	def __init__(self, UMH_Instance):
		self.device = UMH_Instance

		self.begin()

		self.pins = {}

		self.subcommands = {
			"get":b'\x00',
			"set":b'\x01',
			"sap":b'\x70', #Set and add pin
			"gap":b'\x71', #Get and add pin
			"cpin":b'\x7f',
			"manage":b'\xfd',
			"del":b'\xff',
			"add":b'\xfe'
		}

		self.subcommandKeys = {
			"get":[ "pin" ],
			"set":[ "pin", "settings" ],
			"cpin":[ "pin", "settings" ],
			"add":[ "pin", "settings" ],
			"del":[ "pin" ],
			#We need to add sap and gap
		}

		self.pins = {}

	def begin(self):
		if DEBUG == 1:
			print("UARTDigital begin()")
			
		if self.device.running == False:
			print("UART_MH begin() called from UARTDigital")
			self.device.begin()


	def createMessage(self, dataIn):
		if DEBUG:
			print("Entered UARTDigital.createMessage()")

		if "data" not in dataIn:
			return 2

		if "command" not in dataIn or dataIn["command"] not in self.subcommands:
			return 3

		buffer = self.device.assembleHeader("digital")

		#We don't have an extended header, but if we did, it'd go here.

		if dataIn["command"] == "manage":
			buffer = self.lmanage(buffer)
			return buffer
		elif dataIn["command"] == "get":
			buffer = self.lget(buffer, dataIn)
		elif dataIn["command"] == "set":
			buffer = self.lset(buffer, dataIn)
		elif dataIn["command"] == "add":
			buffer = self.ladd(buffer, dataIn)
		elif dataIn["command"] == "del":
			buffer = self.ldel(buffer, dataIn)
		elif dataIn["command"] == "cpin":
			buffer = self.lchange(buffer, dataIn)
		else:
			print("UARTDigital.createMessage(), unknown command: %s" % str(dataIn["command"]))
			return None

		buffer = self.device.finishMessage(buffer)

		if DEBUG:
			print("Returning from UARTDigital.createMessage()")

		return buffer

	def sendMessage(self, buffer):
		return self.device.sendMessage(buffer)

	#pin is the pin
	#pt is 0 for digital, 1 for analog
	def lget(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["get"]
		outLen = to_bytes(1, 2, "little")
		inLen = to_bytes(1, 2, "little")
		buffer[headerOffsets['out_0']] = outLen[0]
		buffer[headerOffsets['out_1']] = outLen[1]
		buffer[headerOffsets['in_0']] = inLen[0]
		buffer[headerOffsets['in_1']] = inLen[1]

		for pinpart in to_bytes(int(dataIn["data"]["pin"]),2):
			buffer.append(pinpart)

		#Since we need to retrieve a message, UARTMessageHandler will need to have something new added.

		return buffer

	#Same as the above, val is for pt=1 0->255, and for pt=0, 0 is low, >0 is high, pt=3 sets pinMode to val
	#State will do nothing yet.
	def lset(self, buffer, dataIn, state=0):
		buffer[headerOffsets["scmd"]] = self.subcommands["set"]
		#Right now, we only support 1 pin at a time... but this will exist for the future.
		outLen = to_bytes(1, 2, "little")
		buffer[headerOffsets['out_0']] = outLen[0]
		buffer[headerOffsets['out_1']] = outLen[1]


		#The two following values will need to be adapted when we accept more than one pin at once.

		#2 bytes for pin
		for pinpart in to_bytes(int(dataIn['data']['pin']), 2):
			buffer.append(pinpart)

		#2 bytes for the setting
		for setpart in to_bytes(int(dataIn['data']['state']), 2):
			buffer.append(setpart)

		return buffer

	def lchange(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["cpin"]		
		buffer[headerOffsets["out_0"]] = b'\x01'

		buffer.append(to_bytes(dataIn['data']['pin'], 2, 0))
		buffer.append(to_bytes(dataIn['data']['direction'], 1, 1))
		buffer.append(to_bytes(dataIn['data']['class'], 1, 1))

		return buffer

	def ladd(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["add"]		
		buffer[headerOffsets["out_0"]] = b'\x01'

		buffer.append(to_bytes(dataIn['data']['pin'], 2, 0))
		buffer.append(to_bytes(dataIn['data']['direction'], 1, 1))
		buffer.append(to_bytes(dataIn['data']['class'], 1, 1))

		self.pins[dataIn['data']['pin']] = { "state":None, "pin":dataIn['data']['pin'], "direction":dataIn['data']['direction'], "class":dataIn['data']['class'] }
		return buffer

	def ldel(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["del"]
		buffer[headerOffsets["out_0"]] = '\x01'

		buffer.append(to_bytes(dataIn['data']['pin'], 2, 0))
		buffer.append(to_bytes(dataIn['data']['pin'], 2, 0))

		if dataIn['data']['pin'] in self.pins:
			del self.pins[dataIn['data']['pin']]

		return buffer

	#This isn't implemented fw-side yet.
	def lmanage(self, buffer):
		if DEBUG:
			print("UARTDigital.lmanage() entered.")

		buffer[headerOffsets["scmd"]] = self.subcommands["manage"]
		buffer[headerOffsets["out_0"]] = b'\x01'


		buffer = self.device.finishMessage(buffer)
		# print("Buffer from lmanage:")
		# pprint.pprint(buffer)
		for i in range(0, 6):
			buffer.append(self.subcommands["manage"])
		
		return self.device.sendManageMessage(buffer)

	def addPin(self, pin):
		self.pins[pin["pin"]] = pin

	def getPin(self, pin):
		if pin in self.pins:
			return self.pins[pin]

		return None

	def digi_manage(self):
		data = {
			"command":"manage",
			"data":{
			}
		}

		return self.createMessage(data)

