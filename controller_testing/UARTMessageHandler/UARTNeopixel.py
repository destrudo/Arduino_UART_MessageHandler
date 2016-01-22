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
import colorsys

from UARTMessageHandler import *
from UARTMessageHandler import isInt
from UARTMessageHandler import to_bytes
from UARTMessageHandler import listOverlay
from UARTMessageHandler import UART_MH

DEBUG=0

# This is a class which handles individual strand data in an easy way
class StrandInfo:
	def __init__(self, id, pin, length):
		self.id = id
		self.pin = pin
		self.length = length
		self.pixels = {}

class UART_Neopixel:
	def __init__(self, UMH_Instance):
		if DEBUG:
			print("In UART_Neopixel constructor.")

		self.device = UMH_Instance

		self.begin()

		self.xheaderOffsets = {
			"id":(len(headerOffsets))
		}

		self.subcommands = {
			"ctrl":b'\x00',
			"ctrli":b'\x01',
			"clear":b'\x02',
			"get":b'\x03',
			"manage":b'\xfd',
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

	#These functions exist to make my life easy so that I don't need to edit the UART_MH methods that get called.
	def begin(self):
		if DEBUG == 1:
			print("UARTNeopixel begin()")
			
		if self.device.running == False:
			print("UART_MH begin() called from UARTNeopixel")
			self.device.begin()

	def finishMessage(self, curMsg):
		return self.device.finishMessage(curMsg)

	def assembleHeader(self, messageType):
		return self.device.assembleHeader(messageType)

	def sendMessage(self, buf):
		return self.device.sendMessage(buf)

	def sendManageMessage(self, buf):
		return self.device.sendManageMessage(buf)

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

		elif dataIn['command'] == "get":
			buffer = self.lget(buffer, dataIn)

		elif dataIn['command'] == "clear":
			buffer = self.lclear(buffer, dataIn)

		elif dataIn['command'] == "manage":
			buffer = self.lmanage(buffer)
			return buffer #this is the only special case.

		elif dataIn['command'] == "add":
			buffer = self.ladd(buffer, dataIn)

		elif dataIn['command'] == "del":
			buffer = self.ldelete(buffer, dataIn)

		else:
			print("UARTNeopixel.createMessage(), Unknown command.")
			return None

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
		buffer[headerOffsets["scmd"]] = self.subcommands["get"]
		buffer[headerOffsets["out_0"]] = b'\x01'
		buffer = self.finishMessage(buffer)

		#buffer.append(dataIn[""]) #id data.

		print("neopixel get ended")

		return buffer


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

	def np_get(self, id, dataIn):
		data = {
			"id":id,
			"command":"get",
			"type":"neopixel",
			"data":[],
		}

		print("np get passed:")
		pprint.pprint(self.sendMessage(self.createMessage(data)))



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


		msgCtd = self.createMessage(data)

		if self.sendMessage(msgCtd):
			print("np_set sendMessage failure.")

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

		#Before passing it down, we should perform checks and remove the ACK.
		return self.createMessage(data)

	def np_gradient(self, id, dataIn):
		#We expect dataIn to have:
		# 'start', the first pixel to use on the strand id
		# 'end', the last pixel to use on the strand id
		# 'startColor', the first color to use, as an RGB list []
		# 'endColor', the last color to use, as an RGB list []

		if "start" not in dataIn:
			print("UART_Neopixel.np_gradient(), no start in dataIn.")
			return None

		if "end" not in dataIn:
			print("UART_Neopixel.np_gradient(), no end in dataIn.")
			return None

		if "startColor" not in dataIn or len(dataIn["startColor"]) != 3:
			print("UART_Neopixel.np_gradient(), no startColor in dataIn.")
			return None

		if "endColor" not in dataIn or len(dataIn["endColor"]) != 3:
			print("UART_Neopixel.np_gradient(), no endColor in dataIn.")
			return None

		#Convert startColor and endColor to HSV values
		startColorHSV = colorsys.rgb_to_hsv(int(dataIn['startColor'][0]),int(dataIn['startColor'][1]),int(dataIn['startColor'][2]))
		endColorHSV = colorsys.rgb_to_hsv(int(dataIn['endColor'][0]),int(dataIn['endColor'][1]),int(dataIn['endColor'][2]))
		#startColorHSV = (0, 255, 0)
		mapSize = int(dataIn["end"]) - int(dataIn["start"])

		#Prepare the data structure
		data = {
			"id":id,
			"command":"ctrl",
			"type":"neopixel",
			"data":{
				"leds":{} #pixel:[r,g,b] sets.
			}
		}

		for nrp in range(0, mapSize):
			lH = (endColorHSV[0] - startColorHSV[0]) * nrp / mapSize + startColorHSV[0]
			lV = (endColorHSV[2] - startColorHSV[2]) * nrp / mapSize + startColorHSV[2]
			lS = (endColorHSV[1] - startColorHSV[1]) * nrp / mapSize + startColorHSV[1]
			#lS = int(startColorHSV[1] + ( (float(mapSize)/float(nrp)) * (endColorHSV[1] - startColorHSV[1]) ) )

			#lRGB = colorsys.hsv_to_rgb(lH, 1., lV)
			lRGB = colorsys.hsv_to_rgb(lH, lS, lV)

			data["data"]["leds"][nrp+int(dataIn["start"])] = [ int(lRGB[0]) % 256, int(lRGB[1]) % 256, int(lRGB[2]) % 256 ]

		if self.sendMessage(self.createMessage(data)):
			print("UART_Neopixel.np_gradient() failed to sendMessage.")