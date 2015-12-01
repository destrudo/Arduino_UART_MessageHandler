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

class UART_Config(UART_MH):
	def __init__(self, serialInterface):
		self.begin(serialInterface)
		pass