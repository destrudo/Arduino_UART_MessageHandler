###############################################################################
#                                UARTConfig.py                                #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#                                                                             #
# This is the configuration library which controls all of the 'base' level    #
#  handling methods for the firmware.                                         #
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

from UARTMessageHandler import *
from UARTMessageHandler import isInt
from UARTMessageHandler import to_bytes
from UARTMessageHandler import listOverlay
from UARTMessageHandler import UART_MH

class UART_Config:
	def __init__(self, UMH_Instance):

		self.device = UMH_Instance

		self.subcommands = {
			"manage":b'\xff'
		}

		self.id = None

		if self.device.running == False:
			self.device.begin()

	def createMessage(self, dataIn):
		if "command" not in dataIn or dataIn["command"] not in self.subcommands:
			return 3

		buffer = self.device.assembleHeader("mhconfig")

		if dataIn['command'] == "manage":
			buffer = self.lmanage(buffer)
			return buffer #special case (And only at time of writing)

		else:
			print("UART_Config.createMessage(), Unknown command.")
			return None

		buffer = self.device.finishMessage(buffer)

		return buffer

	def lmanage(self, buffer):
		buffer[headerOffsets["scmd"]] = self.subcommands["manage"]
		buffer[headerOffsets["out_0"]] = b'\x01' #This should actually call to_bytes and listOverlay.
		buffer = self.device.finishMessage(buffer)

		buffer.append('\x00')

		return self.device.sendManageMessage(buffer)

	def cfg_manage(self):
		data = {
			"command":"manage"
		}

		return self.createMessage(data)