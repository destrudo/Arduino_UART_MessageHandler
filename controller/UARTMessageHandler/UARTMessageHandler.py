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
import multiprocessing

# Debug value
DEBUG=0
# Baud rate default value
BAUD=250000
#BAUD=1000000
# Header data dictionary
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
# Fragmentation response values
g_uart_frag_ok = "CT"
g_uart_frag_bad = "FF"
# Arduino serial fifo size (-1, since we can't actually fill it up.)
arduino_frag_size = 63
arduino_frag_wait_sec = 2

# isInt
#
# @i, type that can be casted to int.
# @ret, true or false depending on the cast ability.
def isInt(i):
	try:
		int(i)
		return True
	except ValueError:
		return False

# to_bytes
#
# @n, integer value
# @length, size in bytes that the integer should become
# @endianess, guess.
def to_bytes(n, length, endianess='big'):
	h = '%x' % n
	s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
	return s if endianess == 'big' else s[::-1]

# listOverlay
#
# @listBase, original list you wish you change.
# @listAdd, list that you want to put on top of listBase
# @offset, index offset you want to start listAdd at.
def listOverlay(listBase, listAdd, offset):
	if DEBUG > 2:
		print("listOverlay listBase:")
		pprint.pprint(listBase)
		print("listOverlay listAdd:")
		pprint.pprint(listAdd)

	for entry in range(0, len(listAdd)):
		if (entry + offset) >= len(listBase): #safety incase of insanity
			listBase.append(listAdd[entry])
		else:
			listBase[entry + offset] = listAdd[entry]

	if DEBUG > 2:
		print("listOverlay complete list:")
		pprint.pprint(listBase)

	return listBase

# lrcsum
#
# @dataIn, list of ints (Less than 255)
# @ret, sum output
def lrcsum(dataIn):
	lrc = 0

	for b in dataIn:
		if DEBUG > 3:
			print("lrcsum data loop: ")
			pprint.pprint(b)

		lrc ^= struct.unpack('B', str(b))[0]

	if DEBUG > 3:
		print("Lrcsum:")
		pprint.pprint(lrc)

	return to_bytes(lrc, 1, 1)

# This is the UART_MH class.  Only one class instance per serial device unless
# you want to see resource conflicts.
class UART_MH:
	def __init__(self):
		pass

	#This should just get moved into the constructor.
	def begin(self, serialInterface):
		if DEBUG:
			print("UART_MH.begin called")
			print(self)

		self.serialSema = multiprocessing.Semaphore()
		#Here we define a bunch of class variables
		self.serialBaud = BAUD #This is the baud rate utilized by the device, we should probably define this higher for easy access.

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

		self.serName = serialInterface
		self.version = 0x00 #We should sort by largest and select the highest one

		self.serialReset()

		if DEBUG:
			print("UART_MH.begin() complete.")

	#  This method performs a hard open/close of the serial device for 
	# situations where calling open() just wasn't enough.
	def serialReset(self):
		if DEBUG:
			print("UART_MH.serialReset() begin")
		if not isinstance(self.ser, serial.Serial):
			try:
				self.ser = serial.Serial(str(self.serName), self.serialBaud, timeout=5)
			except:
				print("UART_MH.serialReset() unable to create new serial instance.")
				return -1
		else: #Otherwise, we /have/ an instance.
			try:
				self.ser.close()
			except:
				pass #We don't care if it failed.

			self.ser = None
			try:
				self.ser = serial.Serial(str(self.serName), self.serialBaud, timeout=5)
			except:
				print("UART_MH.serialReset() unable to create new serial instance from previous instance.")
				return -1

		try:
			if not self.ser.isOpen():
				try:
					self.ser.open()
				except:
					print("UART_MH.serialReset() unable to open serial interface.")
					return -2
		except:
			print("UART_MH.serialReset() unable to call serial.isOpen().")
			return -3

		if DEBUG:
			print("UART_MH.serialReset() complete")
		return 0


	#This prepares the initial message based on the main command type
	def assembleHeader(self,messageType):
		if DEBUG:
			print("UART_MH.assembleHeader() begin")

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

		listOverlay(outBuf, self.mhcommands[messageType], headerOffsets["cmd_0"]) #Shifted the offset over to accomodate the fragment

		if DEBUG > 1:
			print("UART_MH.assembleHeader(), Messagehandler command: %s:" % str(messageType) )
			pprint.pprint(self.mhcommands[messageType])

		if DEBUG:
			print("UART_MH.assembleHeader() complete")

		return outBuf


	#Compute the lrcsum for the message
	def finishMessage(self,curMsg):
		if DEBUG:
			print("UART_MH.finishMessage() begin")


		if len(curMsg) > 63:
			msgFrags = int(math.ceil((float(len(curMsg))/float(63))))
			if (msgFrags <= 255): #If it's in our range, cool, we'll set it.
				curMsg[headerOffsets["msg_frag"]] = to_bytes(msgFrags, 1)
			#If not in range, we'll leave it set to zero.
			print("msgFrags size will be: %d" % msgFrags)

		if DEBUG > 2:
			print("UART_MH.finishMessage(), curMSG Data:")
			pprint.pprint(curMsg)
			print("UART_MH.finishMessage(), curMsg[headerOffsets['sum'] : %s" % str(headerOffsets["sum"]))
		
		#Provided we don't move the sum to some strange place, this should be fine.
		curMsg[headerOffsets["sum"]] = lrcsum(curMsg[:headerOffsets["sum"]])

		if DEBUG:
			print("UART_MH.finishMessage() complete")

		return curMsg

	#wait for uart input to contain expected characters within timeout seconds
	def UARTWaitIn(self, timeout, expected=5):
		if DEBUG:
			print("UART_MH.UARTWaitIn() begin")

		ltimeout = time.time() + timeout
		if not isinstance(self.ser, serial.Serial):
			print("UART_MH.UARTWaitIn(), serial instance does not exist.")
			return -1

		counter = 0

		try:
			while self.ser.inWaiting() < expected : #While we have no input data
				if (counter % 1000) == 0:
					if time.time() > ltimeout:
						return 1
				counter+=1
		except:
			print("UART_MH.UARTWaitIn(), failed to read serial interface.")
			self.ser.flush()
			return -1

		if DEBUG:
			print("UART_MH.UARTWaitIn(), Counter broke at %s", str(counter))

		if DEBUG:
			print("UART_MH.UARTWaitIn() end")

		self.ser.flush()
		return 0


	#This sends the message
	def sendMessage(self,buf):
		t_000 = time.time()
		if DEBUG:
			print("UART_MH.sendMessage(), begin")

		if isinstance(buf, int):
			print("UART_MH.sendMessage(), buffer incomplete.")
			return 1

		if DEBUG == 10:
			print("t_000: %s" % str(time.time() - t_000))
		t_001 = time.time()
	
		self.serialSema.acquire()

		if DEBUG == 10:
			print("t_001: %s" % str(time.time() - t_001))

		t_002 = time.time()

		try:
			if isinstance(self.ser, serial.Serial):
				if not self.ser.isOpen():
					if self.serialReset():
						print("UART_MH.sendMessage(), Serial reset failed.")
						self.serialSema.release()
						return 2
			else:
				if self.serialReset():
					print("UART_MH.sendMessage(), serial create failed.")
					self.serialSema.release()
					return 2

		except:
			print("UART_MH.sendMessage(), failed when polling serial interface.")
			self.serialSema.release()
			return 2

		if DEBUG == 10:
			print("t_002: %s" % str(time.time() - t_002))
	
		t_003 = time.time()

		if DEBUG > 2:
			print("UART_MH.sendMessage() buffer:")
			pprint.pprint(buf)


		msgFrag = struct.unpack('B', str(buf[headerOffsets["msg_frag"]]))[0]

		if DEBUG == 10:
			print("t_003: %s" % str(time.time() - t_003))
	
		t_004 = time.time()

		# If we are using fragmentation for this packet series.
		if (int(msgFrag) > 0):
			chunkTL = 0
			if DEBUG:
				print("UART_MH.sendMessage(), msgFrag is greater than zero")

			#Split the buffer into msg_frag lists 64 elements in size
			packetChunks = [ buf[ x:(x+arduino_frag_size) ] for x in xrange(0, len(buf), arduino_frag_size) ]
	
			if DEBUG == 10:
				print("t_004: %s" % str(time.time() - t_004))
	
			t_005 = time.time()

			for chunk in packetChunks:
				if DEBUG:
					print("New chunk: %s" % str(chunk))
					print("Chunk size: %s" % str(len(chunk)))

				chunkTL = time.time() + arduino_frag_wait_sec #2 seconds to complete each chunk.

				if DEBUG > 2:
					print("\n")
					print("//////////////////////////////////////////////////")
					print("UART_MH.sendMessage(), MsgFrag Chunk: ")
					pprint.pprint(chunk)
					print("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")

				chunkComplete = False

				while not chunkComplete:
					if DEBUG == 10:
						print("Time = %s, chunkTL = %s" % (str(time.time()), str(chunkTL)))
	
					if time.time() > chunkTL:
						print("UART_MH.sendMessage(), chunk send timed out, abandoning attempt.")
						self.serialSema.release()
						return 20

					for b in chunk:
						try:
							self.ser.write(b)
						except:
							print("UART_MH.sendMessage(), failed to write to serial interface with fragment.")
							self.serialSema.release()
							#  If we have a failure to write, it's unlikely that we'll get it on the second pass.
							# Bail out now so that the controller doesn't need to deal with bullshit.
							return 11 

					state = self.ser.readline()

					if state.startswith(g_uart_frag_bad):
						if DEBUG:
							print("UART_MH.sendMessage(), packet chunk send failure, device reports fragment bad.")

						time.sleep(0.1)

					elif state.startswith(g_uart_frag_ok):
						if DEBUG:
							print("UART_MH.sendMessage(), packet chunk send good.")

						chunkComplete = True

						break #We probably don't need the stupid chunkComplete stuff.
			if DEBUG:
				print("Done with chunks.")

			if DEBUG == 10:
				print("t_005: %s" % str(time.time() - t_005))

		# If we are NOT using fragmentation...
		else:
			t_006 = time.time()

			for b in buf:
				try:
					self.ser.write(b)
				except:
					print("UART_MH.sendMessage(), failed to write to serial interface")
					self.serialSema.release()
					return 10

			if DEBUG == 10:
				print("t_006: %s" % str(time.time() - t_006))

		t_007 = time.time()

		if self.UARTWaitIn(2):
			print("UART_MH.sendMessage(), input data timed out.")
			self.serialSema.release()
			return 4

		if DEBUG == 10:
			print("t_007: %s" % str(time.time() - t_007))
	
		t_008 = time.time()

		try:
			retd = self.ser.readline()
		except:
			print("UART_MH.sendMessage(), failed to readline (Response data unknown).")
			self.serialSema.release()
			return 5

		if DEBUG:
			print("UART_MH.sendMessage(), readline response data: ")
			pprint.pprint(retd)

		self.serialSema.release()

		if DEBUG == 10:
			print("t_008: %s" % str(time.time() - t_008))

		if retd.startswith("ACK"):
#			if DEBUG:
			print("UART_MH.sendMessage(), complete (Good)")
			return 0

#		if DEBUG:
		print("UART_MH.sendMessage(), complete (Bad)")

		return 7

	# Send a management message request to the firmware.
	def sendManageMessage(self,buf):
		if DEBUG:
			print("UART_MH.sendManageMessage() called")

		if isinstance(buf, int):
			print("UART_MH.sendManageMessage(), buffer incomplete.")
			return 1

		self.serialSema.acquire()

		try:
			if isinstance(self.ser, serial.Serial):
				if not self.ser.isOpen():
					if self.serialReset():
						print("UART_MH.sendManageMessage(), serial reset failed.")
						self.serialSema.release()
						return 2
			else:
				if self.serialReset():
					print("UART_MH.sendManageMessage(), serial create failed.")
					self.serialSema.release()
					return 2	
		except:
			print("UART_MH.sendManageMessage(), failed when polling serial interface.")
			self.serialSema.release()
			return 2

		if DEBUG > 2:
			print("UART_MH.sendManageMessage(), buffer:")
			pprint.pprint(buf)

		for b in buf:
			try:
				self.ser.write(b)
			except:
				print("UART_MH.sendManageMessage(), failed to write to serial interface")
				self.serialSema.release()
				return 10

		#Custom timing method
		ltimeout = time.time() + 1

		counter = 0

		try:
			#When it opens break
			while not self.ser.inWaiting():
				if (counter % 1000) == 0:
					if time.time() > ltimeout:
						print("UART_MH.sendManageMessage(), timeout in first completion loop.")
						self.serialSema.release()
						return 1
				counter+=1
		except:
			print("UART_MH.sendManageMessage(), failed when waiting for first response.")
			self.serialSema.release()
			return 4

		if DEBUG > 2:
			print("UART_MH.sendManageMessage(), counter break at %s", str(counter))

		ltimeout = time.time() + 1
		complete = False
		counter = 0
		oBuf = ""

		while not complete:
			if (counter % 1000) == 0:
				if time.time() > ltimeout:
					print("UART_MH.sendManageMessage(), timeout in second completion loop.")
					self.serialSema.release()
					return 5

			try:
				while self.ser.inWaiting() > 0:
					oBuf+=self.ser.read(1)
			except:
				print("UART_MH.sendManageMessage(), failed when waiting for second response.")
				self.serialSema.release()
				return 6

			#If we've got at least 5 characters we can start performing the checks....
			if len(oBuf) >= 5:
				if oBuf[-5:].startswith("ACK") or oBuf[:5].startswith("NAK"):
					#We're good (Possibly)
					break

			counter+=1


		if DEBUG > 2:
			print("UART_MH.sendManageMessage(), output buffer: ")
			pprint.pprint(oBuf)

		if DEBUG:
			print("UART_MH.sendManageMessage(), complete")

		self.serialSema.release()

		return oBuf