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

#FIXME, the self.strips var should use this rather than the multilevel dictionary for cleanliness.
class StrandInfo:
	def __init__(self, id, pin, length):
		self.id = id
		self.pin = pin
		self.length = length
		self.pixels = {}

class UART_Neopixel:
	def __init__(self, UMH_Instance):
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
			"get_all":b'\x04',
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

		self.strips = {}



	# begin
	#
	# calls device begin method if it has not yet been run.
	def begin(self):		
		if self.device.running == False:
			self.device.begin()

	# finishMessage
	#
	# Forwards finishMessage call to device finishMessage
	def finishMessage(self, curMsg):
		return self.device.finishMessage(curMsg)

	# assembleHeader
	#
	# Forwards assembleHeader call to device assembleHeader
	def assembleHeader(self, messageType):
		return self.device.assembleHeader(messageType)

	# sendMessage
	#
	# Forwards sendMessage call to device sendMessage
	def sendMessage(self, buf):
		return self.device.sendMessage(buf)

	# sendManageMessage
	#
	# Forwards sendManageMessage call to device sendManageMessage
	def sendManageMessage(self, buf):
		return self.device.sendManageMessage(buf)



	# createMessage
	#
	# @dataIn, dict of data
	# @ret, buffer output from 'selected' command.
	def createMessage(self, dataIn):
		try:
			if "type" not in dataIn: #This probably should be removed.
				return 1

			if "data" not in dataIn:
				return 2

			if "command" not in dataIn or dataIn["command"] not in self.subcommands:
				return 3

			buffer = self.assembleHeader(dataIn["type"])

			buffer.append(to_bytes(dataIn["id"], 1, 1))

			if dataIn["command"] == "ctrl":
				buffer = self.lset(buffer, dataIn)

			elif dataIn["command"] == "ctrli":
				buffer = self.lset(buffer, dataIn, 1)

			elif dataIn["command"] == "get":
				buffer = self.lget(buffer, dataIn)

			elif dataIn["command"] == "get_all":
				buffer = self.lget(buffer, dataIn)

			elif dataIn["command"] == "clear":
				buffer = self.lclear(buffer, dataIn)

			elif dataIn["command"] == "manage":
				buffer = self.lmanage(buffer)
				return buffer #this is the only special case.

			elif dataIn["command"] == "add":
				buffer = self.ladd(buffer, dataIn)

			elif dataIn["command"] == "del":
				buffer = self.ldelete(buffer, dataIn)

			else:
				print("UARTNeopixel.createMessage(), Unknown command was provided: '%s'" % str(dataIn["command"]))
				return None

			buffer = self.finishMessage(buffer)

			return buffer
		except:
			print ("UARTNeopixel.createMessage(), exception with data: '%s'" % str(dataIn))

		return None


	#Message building methods follow.

	# lget
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# lget builds up a get request for the currently active strips
	def lget(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["get"]
		buffer[headerOffsets["out_0"]] = b'\x01'
		buffer = self.finishMessage(buffer)

		return buffer

	def lgetall(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["get_all"]
		buffer[headerOffsets["out_0"]] = b'\x01'
		buffer = self.finishMessage(buffer)

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
		buffer[headerOffsets["scmd"]] = self.subcommands["manage"]
		buffer[headerOffsets["out_0"]] = b'\x01'
		buffer = self.finishMessage(buffer)
		for i in range(0, 6):
			buffer.append(self.subcommands["manage"]) #We want 6 consecutive values of the same command

		return self.sendManageMessage(buffer)

	# lset
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# lset builds up a message for setting pixels to values.
	def lset(self, buffer, dataIn, state=0):
		if state:
			buffer[headerOffsets["scmd"]] = self.subcommands["ctrli"]

		else:
			buffer[headerOffsets["scmd"]] = self.subcommands["ctrl"]

		outLen = to_bytes(len(dataIn['data']['leds']), 2, "little")
		buffer[headerOffsets['out_0']] = outLen[0]
		buffer[headerOffsets['out_1']] = outLen[1]

		for idx in dataIn['data']['leds']:
			for pixelp in to_bytes(int(idx), 2, 1):
				buffer.append(pixelp)

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

	# ladd
	#
	# @buffer, input buffer "string" of bytes
	# @dataIn, dictionary of values
	# @ret, the modified buffer.
	#
	# Prepares a message to add a new strip.
	def ladd(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["add"]
		buffer[headerOffsets["out_0"]] = '\x01'
		buffer.append(to_bytes(dataIn['data']['pin'], 1, 1))

		for b in to_bytes(dataIn['data']['length'], 2, 1):
			buffer.append(b)

		if dataIn["id"] not in self.strips or not isinstance(self.strips[dataIn["id"]], dict):
			self.strips[dataIn["id"]] = {}
			
		self.strips[dataIn["id"]]["pin"] = dataIn['data']['pin']
		self.strips[dataIn["id"]]["length"] = dataIn['data']['length']

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

		buffer.append(buffer[self.xheaderOffsets["id"]])
		buffer.append(buffer[self.xheaderOffsets["id"]])

		if dataIn["id"] in self.strips:
			self.strips[dataIn["id"]] = None

		return buffer





	def np_get(self, id, dataIn):
		data = {
			"id":id,
			"command":"get",
			"type":"neopixel",
			"data":[],
		}

		out = self.sendMessage(self.createMessage(data))

		try:
			if "NAK" in out:
				print("UARTNeopixel.np_get(), error, command failed (NAK)")
				return None
		except:
			errString = "UARTNeopixel.np_get(), error handling output data."
			#pprint.pprint(out)
			if id not in self.strips:
				errString += " strip id %s not found in strips data." % str(id)

			print(errString)
			return None

		out = out[:-5] #Remove the ACK


		#Configure the strips data...
		if id not in self.strips:
			self.strips[id] = { "pin":None, "length":None }

		self.strips[id]["pixels"] = {}

		#Perform a clean format of the strips data.
		counter = 0
		for colGroup in [ out[i:i+4] for i in range(0, len(out), 4) ]:
			self.strips[id]["pixels"][counter] = { "red":colGroup[1], "green":colGroup[2], "blue":colGroup[3] }
			counter+=1

		return self.strips[id]

	def np_get_all(self, id, dataIn):
		data = {
			"id":id,
			"command":"get_all",
			"type":"neopixel",
			"data":[],
		}

		#FIXME, this method is currently in a 'debugging' state.  It does not actually do anything useful.
		pprint.pprint(self.sendMessage(self.createMessage(data)))

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
			print("UARTNeopixel.np_set(), sendMessage call failure.")

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
			print("UARTNeopixel.np_add(), sendMessage call failure.")

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
			print("UARTNeopixel.np_clear(), sendMessage call failure.")

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
			print("UARTNeopixel.np_del(), sendMessage call failure.")

	def np_manage(self):
		data = {
			"id":0,
			"command":"manage",
			"type":"neopixel",
			"data":{
				"id":0
			}
		}

		out = self.createMessage(data)

		try:
			if not out.startswith("NAK"):
				datal = list(out)

				count = struct.unpack("<B", datal.pop(0))[0]

				for i in range(0, count):
					relI = i * 4
					pID = struct.unpack(">B", out[1+relI])[0]
					pin = struct.unpack(">B", out[2+relI])[0]
					length = struct.unpack(">H", out[3+relI:5+relI])[0]

					#The following could be... broken...
					if pID not in self.strips or not isinstance(self.strips[pID], dict):
						self.strips[pID] = { }

					self.strips[pID]["pin"] = pin
					self.strips[pID]["length"] = length 

		except:
			print("UARTNeopixel.np_manage(), issue handling strand instance data.")
			return None

		return out #FIXME, make this baby return self.strips.

	def np_gradient(self, id, dataIn):
		#We expect dataIn to have:
		# 'start', the first pixel to use on the strand id
		# 'end', the last pixel to use on the strand id
		# 'startColor', the first color to use, as an RGB list []
		# 'endColor', the last color to use, as an RGB list []

		if "start" not in dataIn:
			print("UARTNeopixel.np_gradient(), no start in dataIn.")
			return None

		if "end" not in dataIn:
			print("UARTNeopixel.np_gradient(), no end in dataIn.")
			return None

		if "startColor" not in dataIn or len(dataIn["startColor"]) != 3:
			print("UARTNeopixel.np_gradient(), no startColor in dataIn.")
			return None

		if "endColor" not in dataIn or len(dataIn["endColor"]) != 3:
			print("UARTNeopixel.np_gradient(), no endColor in dataIn.")
			return None

		#Convert startColor and endColor to HSV values
		startColorHSV = colorsys.rgb_to_hsv(int(dataIn['startColor'][0]),int(dataIn['startColor'][1]),int(dataIn['startColor'][2]))
		endColorHSV = colorsys.rgb_to_hsv(int(dataIn['endColor'][0]),int(dataIn['endColor'][1]),int(dataIn['endColor'][2]))
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

			lRGB = colorsys.hsv_to_rgb(lH, lS, lV)

			data["data"]["leds"][nrp+int(dataIn["start"])] = [ int(lRGB[0]) % 256, int(lRGB[1]) % 256, int(lRGB[2]) % 256 ]

		if self.sendMessage(self.createMessage(data)):
			print("UARTNeopixel.np_gradient(), sendMessage call failure.")