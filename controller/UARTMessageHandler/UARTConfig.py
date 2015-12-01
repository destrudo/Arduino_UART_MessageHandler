from __future__ import print_function

import serial
import pprint
import sys
import struct
import time
import socket

from UARTMessageHandler import *

#Debug value
DEBUG=0

class UART_Config(UART_MH):
	def __init__(self, serialInterface):
		self.begin(serialInterface)
		pass