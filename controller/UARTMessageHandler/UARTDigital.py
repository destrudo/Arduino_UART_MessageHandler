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

#Debug value
DEBUG=0

class UART_Digital(UART_MH):
	def __init__(self, serialInterface):
		self.begin(serialInterface)

		self.subcommands = {
			"getd":b'\x00',
			"setd":b'\x01',
			"geta":b'\x02',
			"seta":b'\x03',
			"pinm":b'\xff'
		}

	#pin is the pin
	#pt is 0 for digital, 1 for analog
	def lget(self, pin, pt):
		pass

	#Same as the above, val is for pt=1 0->255, and for pt=0, 0 is low, >0 is high, pt=3 sets pinMode to val
	def lset(self, pin, pt, val):
		pass