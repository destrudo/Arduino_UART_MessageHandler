###############################################################################
#                            libUARTMessageHandler                            #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#                                                                             #
###############################################################################
from __future__ import print_function


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

	#leds is a list of leds
	def get(id, leds):
		leds = None

	#leds is a list of leds, colors is the set of colors to use
	def set(id, leds, colors):
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

	#pin is the pin
	#pt is 0 for digital, 1 for analog
	def get(pin, pt):
		pass

	#Same as the above, val is for pt=1 0->255, and for pt=0, 0 is low, >0 is high
	def set(pin, pt, val):
		pass

class UART_MH:
	def __init__(serialInterface):
		#Here we define a bunch of class variables
		serialBaud = 115200

		self.key = 0xAA

		self.commands = {
			"mhconfig":0x00,	#messagehandler configuration command
			"digital":0x01,		#Digital configuration command
			"neopixel":0x02		#NeoPixel configuration command
		}

		self.subcommands = {
			"None":0x00
		}

		self.version = [ 0x00 ] #This variable must be adjusted to accomodate
								# other compatible firmware versions.

		#Header length info
		self.header {
			"key":1,
			"cmd":2,
			"scmd":1,
			"version":1
		}

		self.ser = serial.Serial(str(serialInterface), serialBaud)

	#This sends the message
	def sendMessage(buf):
		for b in buf:
			try:
				self.ser.write(chr(b))
			except:
				print("UART_MH::sendMessage - failed to write to serial interface")

		#Right now, we're using a sleep.  In version 0x01 it'll be a set of 32 0x00's to end a group
		time.sleep(0.15)