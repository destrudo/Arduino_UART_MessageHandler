###############################################################################
#                             UARTMessageHandler.py                           #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#                                                                             #
# This is the 'base' library which handles all of the lowest level stuff.     #
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
import math #We needed the ceil() function.

#Debug value
DEBUG=2
#Baud rate default value
BAUD=250000
#BAUD=115200

def isInt(i):
	try:
		int(i)
		return True
	except ValueError:
		return False

def to_bytes(n, length, endianess='big'):
	h = '%x' % n
	s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
	return s if endianess == 'big' else s[::-1]

def listOverlay(listBase, listAdd, offset):
	if DEBUG > 1:
		print("List input:")
		pprint.pprint(listBase)
		print("Add input:")
		pprint.pprint(listAdd)

	for entry in range(0, len(listAdd)):
		if (entry + offset) >= len(listBase): #safety incase of insanity
			listBase.append(listAdd[entry])
		else:
			listBase[entry + offset] = listAdd[entry]

	if DEBUG > 1:
		print("Ending list:")
		pprint.pprint(listBase)

	return listBase

#This is required for all instances, but quite possibly it should be put into a class and inherited.
headerOffsets = {
	"key_start":0,
	"msg_frag":1,
	"cmd_0":2,
	"cmd_1":3,
	"scmd":4,
	"version":5,
	"out_0":6,
	"out_1":7,
	"in_0":8,
	"in_1":9,
	"sum":10,
	"key_end":11
}

g_uart_frag_ok = "CT"
g_uart_frag_bad = "FF"

# lrcsum
#
# @dataIn, list of ints (Less than 255)
# @ret, sum output
#
def lrcsum(dataIn):

	lrc = 0

	for b in dataIn:
		if DEBUG > 1:
			pprint.pprint(b)

		lrc ^= struct.unpack('B', str(b))[0]

	if DEBUG > 1:
		print("Lrcsum:")
		pprint.pprint(lrc)

	return to_bytes(lrc, 1, 1)


class UART_MH:
	def __init__(self):
		pass

	def begin(self, serialInterface):
		if DEBUG:
			print("UART_MH begin called")

		#Here we define a bunch of class variables
		self.serialBaud = 250000 #This is the baud rate utilized by the device, we should probably define this higher for easy access.

		self.key_start = '\xaa'
		self.key_end = '\xfb'
		self.body_end = '\xdead' #We don't need this at the moment.
		self.uart_frag_ok = "CT"
		self.uart_frag_bad = "FF"

		self.ser = None

		self.mhcommands = {
			"mhconfig":b'\x00\x00', #This isn't used, but  it will be.
			"digital":b'\x01\x00',
			"neopixel":b'\x02\x00',
		}

		self.versions = [ 0x00 ] #This variable must be adjusted to accomodate
								# other compatible firmware versions.

		#Header length info
		self.header = {
			"key_start":1,
			"msg_frag":1,
			"cmd":2,
			"scmd":1,
			"version":1,
			"out":2,
			"in":2,
			"sum":1,
			"key_end":1,
		}

		#Get the total header length based on the above framework.  (Just so that we don't need to change a def if the header changes later)
		self.headerlen = 0
		for item in self.header:
			self.headerlen+=self.header[item]

		#self.npmsg = UART_Neopixel()

		#self.ser = serial.Serial(str(serialInterface), self.serialBaud)
		self.serName = serialInterface

		#At this point we'd be talking to the arduino and getting it's version,
		# then compare it to the valid ones.
		self.version = 0x00 #We should sort by largest and select the highest one

		if DEBUG:
			print("UART_MH Begin complete.")

	#This prepares the initial message based on the main command type
	def assembleHeader(self,messageType):
		outBuf = [
			self.key_start,
			b'\x00',	#This is the fragment set, this needs to be set in finishMessage
			b'\x00',	#These are the two commands, they'll get set afterwards.
			b'\x00',	#cmd 1
			b'\x00',	#subcommand
			to_bytes(self.version, 1, 1), #We always want to present the highest compat version.
			b'\x00',	#out 0
			b'\x00',	#out 1
			b'\x00',	#in 0
			b'\x00',	#in 1
			b'\x00',	#sum, needs to be here as a dummy for the classes to populate via .append()
			self.key_end,
		]

		#WE NEED EXCEPTIONS HERE!
		#As a side effect of the c struct union, we have an endianness problem.  Here and here alone.
		#listOverlay(outBuf, to_bytes(self.mhcommands[messageType], 2, "little"), 1)
		listOverlay(outBuf, self.mhcommands[messageType], headerOffsets["cmd_0"]) #Shifted the offset over to accomodate the fragment

		if DEBUG > 0:
			print("Messagehandler command: %s:" % str(messageType) )
			pprint.pprint(self.mhcommands[messageType])


		#At this point, the message is just about as prepared as we can make it
		# without the class-specific stuff populating the buffer.
		return outBuf


	#Compute the lrcsum for the message
	def finishMessage(self,curMsg):
		if DEBUG:
			print("finishMessage() called.")


		if len(curMsg) > 64:
			msgFrags = int(math.ceil((float(len(curMsg))/float(64))))
			if (msgFrags <= 255): #If it's in our range, cool, we'll set it.
				curMsg[headerOffsets["msg_frag"]] = to_bytes(msgFrags, 1)
			#If not in range, we'll leave it set to zero.

		print("CurMSG Data:")
		pprint.pprint(curMsg)

		#Provided we don't move the sum to some strange place, this should be fine.
		print("curMsg[headerOffsets['sum'] : %s" % str(headerOffsets["sum"]))
		curMsg[headerOffsets["sum"]] = lrcsum(curMsg[:headerOffsets["sum"]])
		return curMsg

	#wait for uart input to contain expected characters within timeout seconds
	def UARTWaitIn(self, timeout, expected=5):
		ltimeout = time.time() + timeout
		if not isinstance(self.ser, serial.Serial):
			print("statusWait called whithout configured and open serial.")
			return -1

		counter = 0

		try:
			while self.ser.inWaiting() != expected : #While we have no input data
				if (counter % 1000) == 0:
					if time.time() > ltimeout:
						return 1
				counter+=1
		except:
			print("UARTWaitIn failed to read serial interface.")
			return -1

		if DEBUG:
			print("Counter broke at %s", str(counter))

		return 0


	#This sends the message
	def sendMessage(self,buf):
		if isinstance(buf, int):
			print("sendMessage buffer incomplete.")
			return 1

		if DEBUG:
			print("INSIDE SENDMESSAGE NOW")

		#self.ser = serial.Serial(str(serialInterface), self.serialBaud)
		try:
			if isinstance(self.ser, serial.Serial):
				if self.ser.isOpen():
					self.ser.close()
		except:
			print("sendMessage failed when cycling serial interface.")
			return 2

		try:
			self.ser = serial.Serial(str(self.serName), self.serialBaud)
		except:
			print("sendMessage failed when opening serial interface.")
			return 3


		if DEBUG:
			print("sendMessage buffer:")
			pprint.pprint(buf)

		#self.ser.open()
		msgFrag = struct.unpack('B', str(buf[headerOffsets["msg_frag"]]))[0]
		if (int(msgFrag) > 0):
			if DEBUG:
				print("MsgFrag is greater than zero")

			#Split the buffer into msg_frag lists 64 elements in size
			packetChunks = [ buf[ x:(x+63) ] for x in xrange(0, len(buf), 63) ]
			for chunk in packetChunks:
				print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
				print("MsgFrag Chunk: ")
				pprint.pprint(chunk)
				print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
				chunkComplete = False
				while not chunkComplete:
					for b in chunk:
						try:
							self.ser.write(b)
						except:
							print("UART_MH::sendMessage - failed to write to serial interface with fragment.")
							#return 11
					state = self.ser.readline()
					if state.startswith(g_uart_frag_bad):
						if DEBUG:
							print("packet chunk send failure, device reports fragment bad.")
						time.sleep(0.5)
					elif state.startswith(g_uart_frag_ok):
						if DEBUG:
							print("packet chunk send good!")
						chunkComplete = True
						break #We probably don't need the stupid chunkComplete stuff.

		else: #Otherwise we've got a buffer size that's not worth computing
			for b in buf:
				try:
					self.ser.write(b)
				except:
					print("UART_MH::sendMessage - failed to write to serial interface")
					return 10

		#Desperately wait for data to be returned from the device.
		#We dynamically adjust this to the number of output commands
		if self.UARTWaitIn(4):
			print("Input data timed out.")
			return 4

		try:
			retd = self.ser.readline()
		except:
			print("Failed to readline!")
			return 5

		if DEBUG:
			pprint.pprint(retd)

		try:
			self.ser.close()
		except:
			print("sendMessage failed to close serial interface.")
			return 6

		if retd.startswith("ACK"):
			if DEBUG:
				print("sendMessage ACK'd")
			return 0

		return 7

		#Right now, we're using a sleep.  In version 0x01 it'll be a set of 32 0x00's to end a group
		#time.sleep(0.15)

	#This will continue reading from the serial interface until it retrieves a NAK or an ACK.
	# It will wait for a maximum of 30 seconds as part of large realistic bounds for configuration.
	# It should return a raw byte array with the same endianess of the UART stream
	#This sends the management message (Supposing it is one)
	def sendManageMessage(self,buf):
		if DEBUG:
			print("SendManageMessage called")
		if isinstance(buf, int):
			print("sendMessage buffer incomplete.")
			return 1

		try:
			if isinstance(self.ser, serial.Serial):
				if self.ser.isOpen():
					self.ser.close()
		except:
			print("sendManageMessage failed when cycling serial interface.")
			return 2

		try:
			self.ser = serial.Serial(str(self.serName), self.serialBaud, timeout=5)
		except:
			print("sendManageMessage failed when opening serial interface.")
			return 3

		if DEBUG:
			print("sendManageMessage buffer:")
			pprint.pprint(buf)

		for b in buf:
			try:
				self.ser.write(b)
			except:
				print("UART_MH::sendManageMessage - failed to write to serial interface")
				return 10

		#Custom timing method
		ltimeout = time.time() + 30

		counter = 0

		try:
			#When it opens break
			while not self.ser.inWaiting():
				if (counter % 1000) == 0:
					if time.time() > ltimeout:
						return 1
				counter+=1
		except:
			print("sendManageMessage failed when waiting for message.")
			return 4

		if DEBUG:
			print("sMgmtMsg Counter 1 broke at %s", str(counter))

		ltimeout = time.time() + 30
		complete = False
		counter = 0
		oBuf = ""

		while not complete:
			if (counter % 1000) == 0:
				if time.time() > ltimeout:
					print("sMgmtMsg timeout 2")
					return 5

			try:
				while self.ser.inWaiting() > 0:
					oBuf+=self.ser.read(1)
			except:
				print("sendManageMessage failed when waiting for second message completion.")
				return 6

			#If we've got at least 5 characters we can start performing the checks....
			if len(oBuf) >= 5:
				if oBuf[-5:].startswith("ACK") or oBuf[:5].startswith("NAK"):
					#We're good (Possibly)
					break

			counter+=1


		if DEBUG:
			pprint.pprint(oBuf)

		try:
			self.ser.close()
		except:
			print("sendManageMessage failed when closing serial interface.")
			return 7

		#Right now, we're using a sleep.  In version 0x01 it'll be a set of 32 0x00's to end a group
		#time.sleep(0.15)
		if DEBUG:
			print("SendManageMessage end")

		return oBuf