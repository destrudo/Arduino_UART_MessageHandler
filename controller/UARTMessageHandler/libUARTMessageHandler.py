###############################################################################
#                            libUARTMessageHandler                            #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#                                                                             #
###############################################################################
from __future__ import print_function

import serial
import pprint
import sys
import struct
import time

DEBUG=0

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
	"key":0,
	"cmd_0":1,
	"cmd_1":2,
	"scmd":3,
	"version":4,
	"out_0":5,
	"out_1":6,
	"in_0":7,
	"in_1":8,
	"sum":9
}

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

	return to_bytes(lrc, 1, 1)


class UART_MH:
	def __init__(self):
		pass

	def begin(self, serialInterface):
		if DEBUG:
			print("UART_MH begin called")

		#Here we define a bunch of class variables
		self.serialBaud = 115200

		self.key = '\xaa'

		self.ser = None

		self.mhcommands = {
			"mhconfig":0x0000,	#messagehandler configuration command
			"digital":0x0001,		#Digital configuration command
			"neopixel":0x0002,		#NeoPixel configuration command
		}

		self.versions = [ 0x00 ] #This variable must be adjusted to accomodate
								# other compatible firmware versions.

		#Header length info
		self.header = {
			"key":1,
			"cmd":2,
			"scmd":1,
			"version":1,
			"out":2,
			"in":2,
			"sum":1
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

	#This prepares the initial message based on the main command type
	def assembleHeader(self,messageType):
		outBuf = [
			self.key,
			b'\x00',	#These are the two commands, they'll get set afterwards.
			b'\x00',	#cmd 1
			b'\x00',	#subcommand
			to_bytes(self.version, 1, 1), #We always want to present the highest compat version.
			b'\x00',	#out 0
			b'\x00',	#out 1
			b'\x00',	#in 0
			b'\x00',	#in 1
			b'\x00'	#sum, needs to be here as a dummy for the classes to populate via .append()
		]

		#WE NEED EXCEPTIONS HERE!
		#As a side effect of the c struct union, we have an endianness problem.  Here and here alone.
		listOverlay(outBuf, to_bytes(self.mhcommands[messageType], 2, "little"), 1)


		#At this point, the message is just about as prepared as we can make it
		# without the class-specific stuff populating the buffer.
		return outBuf


	#Compute the lrcsum for the message
	def finishMessage(self,curMsg):
		curMsg[9] = lrcsum(curMsg[:9])
		return curMsg

	#wait for uart input to contain expected characters within timeout seconds
	def UARTWaitIn(self, timeout, expected=5):
		ltimeout = time.time() + timeout
		if not isinstance(self.ser, serial.Serial):
			print("statusWait called whithout configured and open serial.")
			return -1

		counter = 0
		while self.ser.inWaiting() != expected : #While we have no input data
			if (counter % 1000) == 0:
				if time.time() > ltimeout:
					return 1
			counter+=1

		if DEBUG:
			print("Counter broke at %s", str(counter))

		return 0


	#This sends the message
	def sendMessage(self,buf):
		if isinstance(buf, int):
			print("sendMessage buffer incomplete.")
			return 1

		#self.ser = serial.Serial(str(serialInterface), self.serialBaud)

		if isinstance(self.ser, serial.Serial):
			if self.ser.isOpen():
				self.ser.close()

		self.ser = serial.Serial(str(self.serName), self.serialBaud)

		#self.ser.open()

		if DEBUG:
			print("sendMessage buffer:")
			pprint.pprint(buf)

		for b in buf:
			try:
				self.ser.write(b)
			except:
				print("UART_MH::sendMessage - failed to write to serial interface")
				break

		#Desperately wait for data to be returned from the device.
		#We dynamically adjust this to the number of output commands
		if self.UARTWaitIn(4):
			print("Input data timed out.")
			return 2

		try:
			retd = self.ser.readline()
		except:
			print("Failed to readline!")
			return 3

		if DEBUG:
			pprint.pprint(retd)

		if retd.startswith("ACK"):
			return 0
		else:
			return 4

		self.ser.close()
		#Right now, we're using a sleep.  In version 0x01 it'll be a set of 32 0x00's to end a group
		#time.sleep(0.15)

class UART_Config(UART_MH):
	def __init__(self, serialInterface):
		self.begin(serialInterface)
		pass

class UART_Digital(UART_MH):
	def __init__(self, serialInterface):
		self.begin(serialInterface)

		self.subcommands = {
			"getd":0x00,
			"setd":0x01,
			"geta":0x02,
			"seta":0x03,
			"pinm":0xff
		}

	#pin is the pin
	#pt is 0 for digital, 1 for analog
	def lget(self, pin, pt):
		pass

	#Same as the above, val is for pt=1 0->255, and for pt=0, 0 is low, >0 is high, pt=3 sets pinMode to val
	def lset(self, pin, pt, val):
		pass


class UART_Neopixel(UART_MH):
	def __init__(self, serialInterface):
		self.begin(serialInterface)

		self.xheaderOffsets = {
			"id":(len(headerOffsets))
		}

		self.subcommands = {
			"ctrl":b'\x00',
			"ctrli":b'\x01',
			"clear":b'\x02',
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


	#leds is a list of leds
	def lget(self, buffer, dataIn):
		#We wanna be able to get: id -> pin & length pair
		#						id strip, current color for pixel
		#						id strip, current pixel state (on/off)
		leds = None

	#leds is a list of leds, colors is the set of colors to use
	#state set to anything other than 0 sets the subcmd to ctrli
	def lset(self, buffer, dataIn, state=0):
		if state:
			buffer[headerOffsets["scmd"]] = self.subcommands["ctrli"]
		else:
			buffer[headerOffsets["scmd"]] = self.subcommands["ctrl"]

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

	def lclear(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["clear"]
		buffer[headerOffsets["out_0"]] = '\x01' #default, and tbh, the only valid, is 1.

		return buffer


#	def add(curMsg, id, pin, length):
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

	def ldelete(self, buffer, dataIn):
		buffer[headerOffsets["scmd"]] = self.subcommands["del"]
		buffer[headerOffsets["out_0"]] = '\x01'

		#Delete wants 2 copies after the extended header.
		buffer.append(buffer[self.xheaderOffsets["id"]])
		buffer.append(buffer[self.xheaderOffsets["id"]])

		return buffer


	#The following methods must be part of all inherited UART_MH classes
	def createMessage(self, dataIn):
		if "type" not in dataIn: #This probably should be removed.
			return 1

		if "data" not in dataIn:
			return 2

		if "command" not in dataIn or dataIn["command"] not in self.subcommands:
			return 3

		buffer = self.assembleHeader(dataIn["type"])

		#WE NEED PROPER EXCEPTIONS
		# for key in dataIn['command']:
			# if key not in dataIn["data"]:
				# sys.exit(1)

		#id is required for all commands, and is considered an extended header, so it gets it.
		buffer.append(to_bytes(dataIn["id"], 1, 1))

		if dataIn['command'] == "ctrl":
			buffer = self.lset(buffer, dataIn)

		elif dataIn['command'] == "ctrli":
			buffer = self.lset(buffer, dataIn, 1)

		elif dataIn['command'] == "clear":
			buffer = self.lclear(buffer, dataIn)

		elif dataIn['command'] == "add":
			buffer = self.ladd(buffer, dataIn)

		elif dataIn['command'] == "del":
			buffer = self.ldelete(buffer, dataIn)

		else:
			sys.exit(1) #NEEDS LOCH NESS MONSTERS

		buffer = self.finishMessage(buffer)

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

#This will be the class to handle mqtt messages
class UART_MH_MQTT:
	def __init__(self):
		pass