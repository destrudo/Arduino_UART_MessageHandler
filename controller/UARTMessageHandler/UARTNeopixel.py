###############################################################################
#                               UARTNeopixel.py                               #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#                                                                             #
# This is the Neopixel library portion.  It contains all of the neopixel-     #
#  -specific code.                                                            #
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

DEBUG=0

class UART_Neopixel(UART_MH):
	def __init__(self, serialInterface):
		#self.files_preserve = [handler.socket]
		self.begin(serialInterface)

		self.xheaderOffsets = {
			"id":(len(headerOffsets))
		}

		self.subcommands = {
			"ctrl":b'\x00',
			"ctrli":b'\x01',
			"clear":b'\x02',
			"get":b'\x03', #Not implemented
			"manage":b'\xfd', #Not implemented
			"add":b'\xfe',
			"del":b'\xff'
		}

		self.subcommandKeys = {
			"ctrl":[ "id", "leds"], 
			"ctrli":[ "id", "leds" ],
			"clear":[ "id" ],
			"add":[ "id", "pin", "len"],
			"del":[ "id" ]
		}

		#data[data] should contain a dictionary containing `pixel:{color-red, color-green, color-blue}` sets

		#This variable will be formatted as such:
		# self.strips[id] = {'pin':pin#, 'length':length#}
		self.strips = {}

	#The following method must be part of all inherited UART_MH classes
	def createMessage(self, dataIn):
		if "type" not in dataIn: #This probably should be removed.
			return 1

		if "data" not in dataIn:
			return 2

		if "command" not in dataIn or dataIn["command"] not in self.subcommands:
			return 3

		buffer = self.assembleHeader(dataIn["type"])

		#id is required for all commands, and is considered an extended header, so it gets it.
		buffer.append(to_bytes(dataIn["id"], 1, 1))

		if dataIn['command'] == "ctrl":
			buffer = self.lset(buffer, dataIn)

		elif dataIn['command'] == "ctrli":
			buffer = self.lset(buffer, dataIn, 1)

		elif dataIn['command'] == "clear":
			buffer = self.lclear(buffer, dataIn)

		elif dataIn['command'] == "manage":
			buffer = self.lmanage(buffer)
			return buffer

		elif dataIn['command'] == "add":
			buffer = self.ladd(buffer, dataIn)

		elif dataIn['command'] == "del":
			buffer = self.ldelete(buffer, dataIn)

		else:
			print("Unknown createMessage.")
			sys.exit(1) #NEEDS LOCH NESS MONSTERS

		buffer = self.finishMessage(buffer)

		if DEBUG:
			print("Returning from createMessage()")

		return buffer


	#Message building methods follow.

	# lget
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# lget builds up a get request for the currently active strips
	def lget(self, buffer, dataIn):
		#We wanna be able to get: id -> pin & length pair
		#						id strip, current color for pixel
		#						id strip, current pixel state (on/off)
		leds = None


	# lmanage
	#
	# @buffer, input buffer byte list/string thing
	# @ret, dictionary of data
	#
	# this method is special, in that it automatically calls a special config
	#  method inside UART_MessageHandler to dump all data associated with
	#  this class.  It then returns the output as a dictionary.
	def lmanage(self, buffer):
		if DEBUG:
			print("neopixel lmanage called")
		buffer[headerOffsets["scmd"]] = self.subcommands["manage"]
		buffer[headerOffsets["out_0"]] = b'\x01'
		#buffer[UARTMessageHandler.headerOffsets["scmd"]] = self.subcommands["manage"]
		#buffer[UARTMessageHandler.headerOffsets["out_0"]] = b'\x01'
		buffer = self.finishMessage(buffer)
		#buffer.append(0) #xheader
		#out and in should be disregarded in this case
		for i in range(0, 6):
			buffer.append(self.subcommands["manage"]) #We want 6 consecutive values of the same command

		if DEBUG:
			print("neopixel lmanage ended")

		return self.sendManageMessage(buffer)

	# lset
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# lset builds up a message for setting pixels to values.

	#leds is a list of leds, colors is the set of colors to use
	#state set to anything other than 0 sets the subcmd to ctrli
	def lset(self, buffer, dataIn, state=0):
		if state:
			buffer[headerOffsets["scmd"]] = self.subcommands["ctrli"]
			#buffer[UARTMessageHandler.headerOffsets["scmd"]] = self.subcommands["ctrl"]
		else:
			buffer[headerOffsets["scmd"]] = self.subcommands["ctrl"]
			#buffer[UARTMessageHandler.headerOffsets["scmd"]] = self.subcommands["ctrl"]

		#Set the output length in the header (currently requires non-big)
		outLen = to_bytes(len(dataIn['data']['leds']), 2, "little")
		buffer[headerOffsets['out_0']] = outLen[0]
		buffer[headerOffsets['out_1']] = outLen[1]

		for idx in dataIn['data']['leds']: #This can be anywhere between 
			#The dict should look something like this:
			# blah['data']['leds'][idx] = [ red, green, blue ]

			#The 'pixel' dict index should be an integer
			for pixelp in to_bytes(int(idx), 2, 1): #this splits it into 2
				buffer.append(pixelp)

			#The 'color' dict index should be a list.
			for color in dataIn['data']['leds'][idx]:
				buffer.append(to_bytes(color, 1, 1))

		return buffer

	# lclear
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# Builds the output for clearing a stripid
	def lclear(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["clear"]
		buffer[headerOffsets["out_0"]] = '\x01' #default, and tbh, the only valid, is 1.

		return buffer

	# ldelete
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	def ladd(self, buffer, dataIn):
		#We shoulc probably just copy dataIn['data']* to self.strips[id], doesn't really matter though.
		# self.strips[buffer[self.xheaderOffsets["id"]]] = {
			# "pin":dataIn['data']['pin'],
			# "length":dataIn['data']['length']
		# }

		buffer[headerOffsets["scmd"]] = self.subcommands["add"]
		buffer[headerOffsets["out_0"]] = '\x01'

		#id is already set in prepareMessage()

		buffer.append(to_bytes(dataIn['data']['pin'], 1, 1))
		#buffer = buffer + to_bytes(dataIn['data']['length'], 2) #Hope this works.
		for b in to_bytes(dataIn['data']['length'], 2, 1):
			buffer.append(b)

		#curMsg should now have a near-complete message
		return buffer

	# ldelete
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# This method builds up the message for neopixel strip deletion.
	def ldelete(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["del"]
		buffer[headerOffsets["out_0"]] = '\x01'

		#Delete wants 2 copies after the extended header.
		buffer.append(buffer[self.xheaderOffsets["id"]])
		buffer.append(buffer[self.xheaderOffsets["id"]])

		return buffer


	#The following are the high level, easy access calls

	#id is the stripid, dataIn is a set of "pixel":{red,green,blue} pairs inside a dict
	def np_set(self, id, dataIn):
		data = {
			"id":id,
			"command":"ctrli",
			"type":"neopixel",
			"data": {
				"leds":dataIn
			}
		}

		if DEBUG:
			print("np_set data:")
			pprint.pprint(data)

		if self.sendMessage(self.createMessage(data)):
			print("np_set sendMessage() failed.")

	def np_add(self, id, pin, length):
		data = {
			"id":id,
			"command":"add",
			"type":"neopixel",
			"data":{
				"pin":pin,
				"length":length
			}
		}

		if self.sendMessage(self.createMessage(data)):
			print("np_add sendMessage() failed.")



	def np_clear(self, id):
		data = {
			"id":id,
			"command":"clear",
			"type":"neopixel",
			"data":{
				"id":id,
			}
		}

		if self.sendMessage(self.createMessage(data)):
			print("np_clear sendMessage() failed.")

	def np_del(self, id):
		data = {
			"id":id,
			"command":"del",
			"type":"neopixel",
			"data":{
				"id":id
			}
		}

		if self.sendMessage(self.createMessage(data)):
			print("np_del sendMessage() failed.")

	def np_manage(self):
		data = {
			"id":0,
			"command":"manage",
			"type":"neopixel",
			"data":{
				"id":0
			}
		}

		return self.createMessage(data)