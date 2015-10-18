###############################################################################
#                            libUARTMessageHandler                            #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#                                                                             #
###############################################################################
from __future__ import print_function

def to_bytes(n, length, endianess='big'):
	h = '%x' % n
	s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
	return s if endianess == 'big' else s[::-1]

def listOverlay(listBase, listAdd, offset)
	for entry in range(0, len(listAdd)):
		if (entry + offset) >= len(listBase): #safety incase of insanity
			listBase.append(listAdd[entry])
		else:
			listBase[entry + offset] = listAdd[entry]

	return listBase

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
		lrc ^= b

	return lrc

class UART_Digital:
	def __init__():
		self.subcommands = {
			"getd":0x00,
			"setd":0x01,
			"geta":0x02,
			"seta":0x03,
			"pinm":0xff
		}

	#pin is the pin
	#pt is 0 for digital, 1 for analog
	def get(pin, pt):
		pass

	#Same as the above, val is for pt=1 0->255, and for pt=0, 0 is low, >0 is high, pt=3 sets pinMode to val
	def set(pin, pt, val):
		pass


class UART_Neopixel:
	def __init__():
		self.subcommands = {
			"ctrl":0x00,
			"ctrli":0x01,
			"clear":0x02,
			"add":0xfe,
			"del":0xff
		}

		self.subcommandKeys = {
			"ctrl":[ "id", "leds"], 
			"ctrli":[ "id", "leds" ],
			"clear":[ "id" ],
			"add":[ "id", "pin", "len"],
			"del":[ "id" ]
		}

		#data[data] should contain a dictionary containing `pixel:{color-red, color-green, color-blue}` sets

		self.strips = {}


	#leds is a list of leds
	def get(id, leds):
		leds = None

	#leds is a list of leds, colors is the set of colors to use
	#state set to anything other than 0 sets the subcmd to ctrli
	def set(id, leds, colors, state=0):
		pass

	def clear(id):
		pass

	def add(curMsg, id, pin, length):
		curMsg[headerOffsets["scmd"]] = self.subcommands[add]
		curMsg[headerOffsets["out_0"]] = 0x01
		self.strips[id] = { "pin":pin, "len":length }
		#curMsg should now have a near-complete message
		buf.append(

	def delete(id):
		pass

	def prepareMessage(buffer, dataIn):
		pass

class UART_MH:
	def __init__(serialInterface):
		#Here we define a bunch of class variables
		serialBaud = 115200

		self.key = '\xaa'

		self.commands = {
			"mhconfig":0x0000,	#messagehandler configuration command
			"digital":0x0001,		#Digital configuration command
			"neopixel":0x0002		#NeoPixel configuration command
		}

		#Command class definitions
		self.commandC = {
			"neopixel":UART_Neopixel(),
			"digital":UART_Digital()
		}

		self.subcommands = {
			"None":0x00
		}

		self.versions = [ 0x00 ] #This variable must be adjusted to accomodate
								# other compatible firmware versions.

		#Header length info
		self.header {
			"key":1,
			"cmd":2,
			"scmd":1,
			"version":1
			"out":2,
			"in":2,
			"sum":1
		}

		#Get the total header length based on the above framework.
		self.headerlen = 0
		for item in self.header:
			self.headerlen+=self.header[item]

		self.npmsg = UART_Neopixel()

		self.ser = serial.Serial(str(serialInterface), serialBaud)

		#At this point we'd be talking to the arduino and getting it's version,
		# then compare it to the valid ones.
		self.version = 0x00

	#This prepares the initial message based on the main command type
	def prepMessage(messageType):
		outBuf = [
			self.key,
			'\x00',	#These are the two commands, they'll get set afterwards.
			'\x00',	#cmd 1
			'\x00',	#subcommand
			to_bytes(self.version,1), #We always want to present the highest compat version.
			'\x00',	#out 0
			'\x00',	#out 1
			'\x00',	#in 0
			'\x00',	#in 1
			'\x00'	#sum, needs to be here as a dummy for the classes to populate via .append()
		]

		#WE NEED EXCEPTIONS HERE
		listOverlay(outBuf, to_bytes(self.commands[messageType], 2), 1)

		#At this point, the message is just about as prepared as we can make it
		# without the class-specific stuff populating the buffer.
		return outBuf


	#Compute the lrcsum for the message
	def finishMessage(curMsg):
		curMsg[9] = lrcsum(curMsg[:9])
		return curMsg

	def createMessage(dataIn):
		# dataIn must be a dictionary which has these values set:
		if "type" not in dataIn:
			return 1
		if dataIn["type"] not in self.commands:
			return 1

		#Make sure the command is in the class subcommands
		if "command" not in dataIn:
			return 2
		if dataIn["command"] not in self.commandC[dataIn["type"]].subcommands:
			return 2

		#Make sure our data dict is configured
		if "data" not in dataIn:
			return 3

		buf = prepMessage(dataIn["type"])
		#Call the class-specific stuff.
		buf = self.commandC[dataIn["type"]].prepareMessage(buf, dataIn)

		#Finish it off
		buf = finishMesage(buf)

		return buf

	#This sends the message
	def sendMessage(buf):
		for b in buf:
			try:
				self.ser.write(chr(b))
			except:
				print("UART_MH::sendMessage - failed to write to serial interface")

		#Right now, we're using a sleep.  In version 0x01 it'll be a set of 32 0x00's to end a group
		time.sleep(0.15)

#This will be the class to handle mqtt messages
class UART_MH_MQTT:
	def __init__():
		pass