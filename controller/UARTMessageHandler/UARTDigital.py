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

#FIXME, the self.pins var should use this rather than dicts
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



	# begin
	#
	# calls device begin method if it has not yet been run
	def begin(self):
		if self.device.running == False:
			self.device.begin()



	# createMessage
	#
	# @dataIn, dict of data
	# @ret, buffer output from 'selected' command.
	def createMessage(self, dataIn):
		try:
			if "data" not in dataIn:
				return 2

			if "command" not in dataIn or dataIn["command"] not in self.subcommands:
				return 3

			buffer = self.device.assembleHeader("digital")

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
				print("UARTDigital.createMessage(), Unknown command was provided: '%s'" % str(dataIn["command"]))
				return None

			buffer = self.device.finishMessage(buffer)

			return buffer
		except:
			print("UARTDigital.createMessage(), exception with data: '%s'" % str(dataIn))

		return None

	# sendMessage
	#
	# @buffer, input buffer "string" of bytes
	# @ret, the output buffer from the device sendMessage call.
	#
	# Forwards a sendMessage call to the device sendMessage method.
	def sendMessage(self, buffer):
		return self.device.sendMessage(buffer)

	# lget
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# lget builds up a get request for the pin selected.
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

		return buffer

	# lset
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# lset builds up a message for setting pin values.
	def lset(self, buffer, dataIn, state=0):
		buffer[headerOffsets["scmd"]] = self.subcommands["set"]
		#Right now, we only support 1 pin at a time... but this will exist for the future.
		outLen = to_bytes(1, 2, "little")
		buffer[headerOffsets['out_0']] = outLen[0]
		buffer[headerOffsets['out_1']] = outLen[1]

		for pinpart in to_bytes(int(dataIn['data']['pin']), 2):
			buffer.append(pinpart)

		for setpart in to_bytes(int(dataIn['data']['state']), 2):
			buffer.append(setpart)

		return buffer

	# lset
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# lset builds up a message for changing the mode of a pin.
	def lchange(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["cpin"]		
		buffer[headerOffsets["out_0"]] = b'\x01'

		buffer.append(to_bytes(dataIn['data']['pin'], 2, 0))
		buffer.append(to_bytes(dataIn['data']['direction'], 1, 1))
		buffer.append(to_bytes(dataIn['data']['class'], 1, 1))

		return buffer

	# ladd
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# Prepare message to add a new pin
	def ladd(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["add"]		
		buffer[headerOffsets["out_0"]] = b'\x01'

		buffer.append(to_bytes(dataIn['data']['pin'], 2, 0))
		buffer.append(to_bytes(dataIn['data']['direction'], 1, 1))
		buffer.append(to_bytes(dataIn['data']['class'], 1, 1))

		self.pins[dataIn['data']['pin']] = { "state":None, "pin":dataIn['data']['pin'], "direction":dataIn['data']['direction'], "class":dataIn['data']['class'] }
		return buffer

	# ldel
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# Prepare message to delete a new pin
	def ldel(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["del"]
		buffer[headerOffsets["out_0"]] = '\x01'

		buffer.append(to_bytes(dataIn['data']['pin'], 2, 0))
		buffer.append(to_bytes(dataIn['data']['pin'], 2, 0))

		if dataIn['data']['pin'] in self.pins:
			del self.pins[dataIn['data']['pin']]

		return buffer

	# lmanage
	#
	# @buffer, input buffer "string" of bytes
	# @ret, output buffer (SendManageMessage happens here.)
	#
	# Prepare and then send a management message, and then return the output.
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




		
	# digi_manage
	#
	# @ret, output of the manage call.
	#
	# Performs management call to createMessage and then returns the output data.
	def digi_manage(self):
		data = {
			"command":"manage",
			"data":{
			}
		}

		return self.createMessage(data)