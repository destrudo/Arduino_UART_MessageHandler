###############################################################################
#                                MQTTHandler.py                               #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#  utilizing an mqtt client.                                                  #
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
import copy

#Separating this because when I move the module out it'll be happier.
import paho.mqtt.client as mqtt
import multiprocessing

from UARTMessageHandler import *
#from UARTMessageHandler import UART_MH
from UARTConfig import *
from UARTDigital import *
from UARTNeopixel import *

DEBUG = 0
VERBOSE = 0

MSG_HOST_OFFSET = 1
MSG_SERVICE_OFFSET = 2
MSG_ID_OFFSET = 3
MSG_CLASS_OFFSET = 4
MSG_STRAND_OFFSET = 5 #This doubles as the add offset.
MSG_COMMAND_OFFSET = 6
MSG_PIXEL_OFFSET = 7

#Digital utilized data

MSG_PIN_OFFSET = 5 #Doubles as add offset
MSG_PIN_CMD_OFFSET = 6

#OUTPUT = 1
#INPUT = 0
#HIGH = 1
#LOW = 0

DIGITAL_MSG_CONTENT = {
	"direction":{
		#Output stuff
		"output":OUTPUT,
		"out":OUTPUT,
		"1":OUTPUT,
		#Input stuff
		"input":INPUT,
		"in":INPUT,
		"0":INPUT,
	},
	"state":{
		"high":HIGH,
		"low":LOW,
	},
	"class":{
		"digital":C_DIGITAL,
		"0":C_DIGITAL,
		"analog":C_ANALOG,
		"1":C_ANALOG,
	},
	"get":{
		1:"high",
		0:"low",
	}
}

#Device class ID (For device differentiation)
SERVICEID="uartmh"

#Separating this because when I move the module out it'll be happier.
MQTTPROCESSTIMEOUT = 1
MQTTPROCESSTIMELIMIT = 120

class UARTDevices:
	def __init__(self, port, baud=BAUD):
		self.port = port
		self.baud = baud
		self.id = None
		self.UMHI = None #Here we want to actually create the 


#This will be the class to handle mqtt messages
class UART_MH_MQTT:
	def __init__(self,hostname,port):
		self.hostname = str(socket.gethostname())
		self.devices = {}

		self.client = mqtt.Client(client_id="uart-mh@%s" % self.hostname)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.max_inflight_messages_set(100);
		self.client.connect(hostname, port, 10)
		self.messageHandlers = {}

		self.neopixelBuffer = {}
		self.timeElapsed = 0
		self.timeMax = 200 #(ms)

		self.threadInstances = {}
		self.threadInstancePipes = {}
		self.busyThreadBuffer = {}

		#self.threadSema = multiprocessing.Semaphore()
		#self.threadSema.release()
		self.threadPostSema = multiprocessing.Semaphore()
		self.threadPostSema.release()

	def has_instance(self, name, id):
		if len(self.devices) == 0:
			return False

		if id not in self.devices:
			return False

		if str(name) not in self.devices[id]:
			return False

		return True

	def add_instance(self, name, instance):
		self.messageHandlers[name] = instance

	def add_instance(self, name, instance, id):
		if not id:
			print("UART_MH_MQTT.add_instance, got no ID.")
			return None

		if id not in self.devices:
			if name is not "mhconfig":
				print("UART_MH_MQTT.add_instance, not configured device and instance was not mhconfig.")
				return None

			self.devices[id] = {}
			self.devices[id][name] = instance

		else:
			if "mhconfig" not in self.devices[id]: #Triple check so we know if we have some oddity.
				print("UART_MH_MQTT.add_instance, strangely misconfigured device id: %s" % str(id))

			if name in self.devices[id]: #Issue a warning that we're overwriting the old device instance
				print("UART_MH_MQTT.add_instance, device->instance name already in use.  Replacing it.")

			self.devices[id][name] = instance

		return True

	def add_device(self, config):
		pass

	def on_connect(self, client, userdata, flags, rc):
		self.client.subscribe("/%s/#" % self.hostname, 0)
		# We're looking at a structure like this:
		# %hostname%/neopixel
		# %hostname%/neopixel/%strandid%/
		# %hostname%/neopixel/%strandid%/set/
		# %hostname%/neopixel/%strandid%/set/%led% = (r,g,b)
		# %hostname%/neopixel/%strandid%/config = [ o, old data| f, fresh data | u, unknown ] #This is a published path
		# %hostname%/neopixel/%strandid%/config/pin = value
		# %hostname%/neopixel/%strandid%/config/length = value
		# %hostname%/neopixel/%strandid%/config/leds/%led% = (r,g,b)
		# %hostname%/neopixel/add = (%strandid%,%pin%,%len%)
		# %hostname%/digital/%pin%/aset/%value% #This value gets set
		# %hostname%/digital/%pin%/aget #After setting any value to this dir, value/%val% will be published
		# %hostname%/digital/%pin%/get #After setting any value to this dir, value/%val% will be published
		# %hostname%/digital/%pin%/set/%value% #this value gets set
		# %hostname%/digital/%pin%/value/%val% #This is published to
		# %hostname%/control

#RENAME MULTISET TO THIS.
	#This is the worker thread to be which waits for timeMax or a send command to be reached
	def neopixel_set_t(self):
		#Get current time
		#if (current time) == (lastTime + timeMax):
		#	send data
		pass

	#Note: This can be simplified in the future by actually applying the common method names for each class type.
	def on_message(self, client, userdata, msg):
		if VERBOSE:
			print("UART_MH_MQTT.on_message() begin.")
		if DEBUG:
			print("################################################")
			print("MQTT on_message msg message:")
			pprint.pprint(msg.payload)
			print("MQTT on_message msg topic:")
			pprint.pprint(msg.topic)
			print("MQTT on_message msg qos:")
			pprint.pprint(msg.qos)

		#We don't want to do any processing on */config* messages
		if "/config" in msg.topic:
			if DEBUG:
				print("mqtt configuration message, ignoring.")
			return None

		#Here we purge data that has nothing to do
		try:
			msgIdent = msg.topic.split("/")[3]

			if msgIdent not in self.devices:
				print("UART_MH_MQTT.on_message, ident [%s] not in devices." % str(msgIdent))
				return None
		except:
			return None

		msgL = msg.topic.split("/")

		#for neopixel
		if "neopixel" in msg.topic and "neopixel" in self.devices[msgIdent]:
			if DEBUG:
				print("neopixel mqtt message.")

			if DEBUG == 2:
				print("MsgL data:")
				pprint.pprint(msgL)

			if len(msgL) < 5:
				print("Bogus neopixel message received. [incomplete data]")
				return None

			#Make sure that we've gotten a sane response.
			if isInt(msgL[MSG_STRAND_OFFSET]):
				if (int(msgL[MSG_STRAND_OFFSET]) > 254) or (int(msgL[MSG_STRAND_OFFSET]) < 0):
					print("Bogus neopixel message received. [strand id error]")
					return None
			else:
				#if (msgL[3] != "add") and (msgL[3] != "del") and (msgL[3] != "clear"):
				if (msgL[MSG_STRAND_OFFSET] != "add"):
					print("Bogus neopixel message received. [unexpected topic '%s']" % str(msgL[4]))
					return None

			#This is the only instance where a strand ID is not specified (Since it won't exist until this is called)
			if msgL[MSG_STRAND_OFFSET] == "add":
				if DEBUG:
					print("neopixel mqtt message [add]")

				data = msg.payload.split(",")
#CHECK THIS
				if len(data) != 3:
					print("Bogus neopixel message received. [add missing data]")
					return None

				if DEBUG:
					print("neopixel mqtt adding [id:%s,pin:%s,len:%s]" % (data[0], data[1], data[2]))

				umhmsg = {
					"id":int(data[0]),
					"command":"add",
					"type":"neopixel",
					"data":{
						"pin":int(data[1]),
						"length":int(data[2]),
					}
				}

				if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(umhmsg)):
					print("neopixel mqtt issue sending message.")

				return None #After this we want to leave.

			#If we have one of the initiation commands
			#FIXME, pretty sure this should be >= 7 !!!
			if len(msgL) >= 6:
				#FIXME, This is the starting point for the revised neopixel mqtt stuff.
				# umhmsg = {
				# 	"id":int(msgL[MSG_STRAND_OFFSET]),
				# 	"type":"neopixel",
				# }

				if msgL[MSG_COMMAND_OFFSET] == "set" or msgL[MSG_COMMAND_OFFSET] == "seti": #Set commands handler
					rgbS = msg.payload.split(",")
					rgbI = []

					for sv in rgbS:
						rgbI.append(int(sv))

					for iChk in rgbS:
						if iChk == "" or iChk == None: #If we have a blank message.
							print("neopixel mqtt blank message.")
							return None

						if int(iChk) < 0 or int(iChk) > 255:
							print("neopixel mqtt message outside int limits.")
							return None

					umhmsg = {
						"id":int(msgL[MSG_STRAND_OFFSET]),
						"command":"ctrl",
						"type":"neopixel",
						"data":{
							"leds":{ str(msgL[MSG_PIXEL_OFFSET]):rgbI }
						}
					}

					if msgL[MSG_COMMAND_OFFSET] == "seti":
						umhmsg["command"] = "ctrli"

						if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(umhmsg)):
							print("neopixel mqtt seti issue sending message.")

						return None


					if int(msgL[MSG_STRAND_OFFSET]) not in self.threadInstances:
						self.threadInstancePipes[int(msgL[MSG_STRAND_OFFSET])] = multiprocessing.Pipe()

						if int(msgL[MSG_STRAND_OFFSET]) in self.busyThreadBuffer:
							if len(self.busyThreadBuffer[msgL[MSG_STRAND_OFFSET]]) > 0:
								for data in self.busyThreadBuffer[msgL[MSG_STRAND_OFFSET]]:
									for part in data['data']:
										umhmsg['data'][part] = data['data'][part]

							self.busyThreadBuffer.pop(int(msgL[MSG_STRAND_OFFSET]), None)

						self.threadInstances[int(msgL[MSG_STRAND_OFFSET])] = multiprocessing.Process(target=self.multiSet, args=(umhmsg, self.threadInstancePipes[int(msgL[MSG_STRAND_OFFSET])], copy.copy(msgIdent), MQTTPROCESSTIMEOUT, MQTTPROCESSTIMELIMIT,))
						self.threadInstances[int(msgL[MSG_STRAND_OFFSET])].start()
						
						return None #Break out completely, we don't want to do anything else.

					#Call a join
					try:
						self.threadInstances[int(msgL[MSG_STRAND_OFFSET])].join(0.005)
					except:
						pass

					if self.threadInstances[int(msgL[MSG_STRAND_OFFSET])].is_alive(): #If it's been started.
						if not self.threadPostSema.acquire(False): #If threadPostSema is currently blocking
							if not int(msgL[MSG_STRAND_OFFSET]) in self.busyThreadBuffer:
								self.busyThreadBuffer[int(msgL[MSG_STRAND_OFFSET])] = []

							self.busyThreadBuffer[int(msgL[MSG_STRAND_OFFSET])].append(copy.copy(umhmsg))

						else:
							self.threadInstancePipes[int(msgL[MSG_STRAND_OFFSET])][1].send(umhmsg)

						self.threadPostSema.release() #Release no matter what.

					else:
						self.threadInstancePipes[int(msgL[MSG_STRAND_OFFSET])] = None

						self.threadInstances[int(msgL[MSG_STRAND_OFFSET])].terminate()
						self.threadInstances[int(msgL[MSG_STRAND_OFFSET])] = None

						self.threadInstancePipes[int(msgL[MSG_STRAND_OFFSET])] = multiprocessing.Pipe()
						self.threadInstances[int(msgL[MSG_STRAND_OFFSET])] = multiprocessing.Process(target=self.multiSet, args=(umhmsg, self.threadInstancePipes[int(msgL[MSG_STRAND_OFFSET])], msgIdent, MQTTPROCESSTIMEOUT, MQTTPROCESSTIMELIMIT,))
						self.threadInstances[int(msgL[MSG_STRAND_OFFSET])].start()

				elif msgL[MSG_COMMAND_OFFSET] == "del": #deletion command
					if msg.payload != msgL[MSG_STRAND_OFFSET]:
						print("neopixel mqtt del command issued with mismatched payload. [%s,%s]" % ( str(msgL[MSG_STRAND_OFFSET]), str(msg.payload) ) )
						return None

					umhmsg = {
						"id":int(msgL[MSG_STRAND_OFFSET]),
						"command":"del",
						"type":"neopixel",
						"data":{
							"id":int(msg.payload) #I could just use msgL[3], but it seems more useful.
						}
					}

					if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(umhmsg)):
						print("neopixel mqtt issue sending del message.")

				if msgL[MSG_COMMAND_OFFSET] == "gradient":
					data = msg.payload.split(",")
					# 0 is start
					# 1 is startR
					# 2 is startG
					# 3 is startB
					# 4 is end
					# 5 is endR
					# 6 is endG
					# 7 is endB
					start = data[0]
					end = data[4]
					sRGB = data[1:4]
					eRGB = data[5:8]

					umhmsg = {
						"start":start,
						"end":end,
						"startColor":sRGB,
						"endColor":eRGB,
					}

					if self.devices[msgIdent]["neopixel"].np_gradient(int(msgL[MSG_STRAND_OFFSET]),umhmsg):
						print("bad gradient.")

				elif msgL[MSG_COMMAND_OFFSET] == "clear":
					# if msg.payload != msgL[MSG_STRAND_OFFSET]: #This should get nuked later.
					# 	print("neopixel mqtt clear command issued with mismatched payload. [%s,%s]" % ( str(msgL[MSG_STRAND_OFFSET]), str(msg.payload) ) )
					# 	return None
					
					umhmsg = {
						"id":int(msgL[MSG_STRAND_OFFSET]),
						"command":"clear",
						"type":"neopixel",
						"data":{
							"id":int(msg.payload) #I could just use msgL[3], but it seems more useful.
						}
					}

					if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(umhmsg)):
						print("neopixel mqtt issue sending clear message.")

		elif "digital" in msg.topic and "digital" in self.devices[msgIdent]:
			if len(msgL) < 5:
				print("Bogus digital message received.")
				return None

			if isInt(msgL[MSG_PIN_OFFSET]):
				if (int(msgL[MSG_PIN_OFFSET]) > 254) or (int(msgL[MSG_PIN_OFFSET]) < 0):
					print("Bogus digital message received. [pin error]")
					return None

			else:
				if (msgL[MSG_PIN_OFFSET] != "add"):
					print("Bogus digital message received. [unexpected topic: %s]" % str(msgL[MSG_PIN_OFFSET]))
					return None

			if msgL[MSG_PIN_OFFSET] == "add":
				data = msg.payload.split(",")
				if (len(data) < 3) or (len(data) > 4):
					print("Bogus digital message received. [incorrect number of values in add command]")
					return None

				umhmsg = {
					"pin":int(data[0]),
					"command":"add",
					"type":"digital",
					"data":{
						"pin":int(data[0]),
						"direction":int(data[1]),
						"class":int(data[2]),
					}
				}

				if len(data) == 4:
					if umhmsg["data"]["direction"] == 1:
						umhmsg["command"] = "sap"
						umhmsg["data"]["state"] = int(data[3])
					#We don't yet want to support gap, but when we do, it'll be here.

				if self.devices[msgIdent]["digital"].sendMessage(self.devices[msgIdent]["digital"].createMessage(umhmsg)):
					print("digital mqtt issue sending add message.")

			if len(msgL) == 7:

				umhmsg = {
					"pin":int(msgL[MSG_PIN_OFFSET]),
					"type":"digital",
				}

				if msgL[MSG_PIN_CMD_OFFSET] == "direction" or msgL[MSG_PIN_CMD_OFFSET] == "class":
					pinData = self.devices[msgIdent]["digital"].getPin(int(msgL[MSG_PIN_OFFSET]))
					if not pinData:
						return None
					#change local pin direction
					umhmsg["data"] = pinData
					if msg.payload.lower() not in DIGITAL_MSG_CONTENT[msgL[MSG_PIN_CMD_OFFSET]]:
						print("digital mqtt issue with direction message, content: %s" % str(msg.payload) )
						return None

					#convert local pin mode data to umhmsg
					umhmsg["data"][msgL[MSG_PIN_CMD_OFFSET]] = DIGITAL_MSG_CONTENT[msgL[MSG_PIN_CMD_OFFSET]][msg.payload.lower()]
					self.devices[msgIdent]["digital"].addPin(umhmsg["data"])

					umhmsg["command"] = "cpin"
					#call cpin
					if self.devices[msgIdent]["digital"].sendMessage(self.devices[msgIdent]["digital"].createMessage(umhmsg)):
						print("digital mqtt issue sending %s message." % str(msgL[MSG_PIN_OFFSET]))
					
				elif msgL[MSG_PIN_CMD_OFFSET] == "state" or msgL[MSG_PIN_CMD_OFFSET] == "set" :
					pinData = self.devices[msgIdent]["digital"].getPin(int(msgL[MSG_PIN_OFFSET]))
					if not pinData:
						print("No pin data!")
						return None
					
					umhmsg["data"] = pinData
					if isInt(msg.payload):
						umhmsg["data"]["state"] = int(msg.payload)
					elif msg.payload.lower() in DIGITAL_MSG_CONTENT["state"]:
						umhmsg["data"]["state"] = DIGITAL_MSG_CONTENT["state"][msg.payload.lower()]
					else:
						print("digital mqtt issue with direction message, content: %s" % str(msg.payload) )
						return None

					umhmsg["command"] = "set"
					#call cpin
					if self.devices[msgIdent]["digital"].sendMessage(self.devices[msgIdent]["digital"].createMessage(umhmsg)):
						print("digital mqtt issue sending direction message.")

				elif msgL[MSG_PIN_CMD_OFFSET] == "get":
					ltopic = "/%s/%s/%s" % ( str(self.hostname), str(SERVICEID), str(msgIdent) )
					pinData = self.devices[msgIdent]["digital"].getPin(int(msgL[MSG_PIN_OFFSET]))
					umhmsg["command"] = "get"
					umhmsg["data"] = pinData

					retData = self.devices[msgIdent]["digital"].sendMessage(self.devices[msgIdent]["digital"].createMessage(umhmsg))
					pinData["state"] = struct.unpack("<h",retData[0:2])[0]

					self.client.publish("%s/digital/%s/config/state" % ( str(ltopic), str(pinData["pin"]) ), str(pinData["state"]))
					self.devices[msgIdent]["digital"].addPin(pinData)
				else:
					print("Bogus digital mqtt topid for cmd offset: %s" % str(msgL[MSG_PIN_CMD_OFFSET]))
					return None

		else:
			print("Unknown topic")

		if VERBOSE:
			print("UART_MH_MQTT.on_message() complete.")

	#This is for set commands which support more than one command at the same time (Thus the need to concat a bunch of commands together.)
	def multiSet(self, setDictI, pipeD, msgIdent, timeout, timeLimit):
		cTimeout = time.time() + timeout
		cTimeLimit = time.time() + timeLimit

		if DEBUG:
			print("### MULTISET ENTERED WITH setDictI: %s" % str(setDictI))

		while ( (time.time() < cTimeout) and time.time() < cTimeLimit and pipeD != None ):
			if pipeD[0].poll(0.02): #We'll poll for a second (Since it has little bearing on the world)
				dIn = pipeD[0].recv()
				if DEBUG:
					print("### multiSet got message in pipe: %s" % str(dIn))

				#No matter the message, we should extend the time limit.
				cTimeout = time.time() + timeout

				if isinstance(dIn, str): #If we have one of the request inputs [NI]
					#Do things for single string
					continue

				if not isinstance(dIn, dict):
					if DEBUG:
						print("### multiSet didn't get dict post string check.")
					continue

				if setDictI['type'] == "neopixel":
					if DEBUG:
						print("MultiSet while type neopixel.")
	
					if len(dIn) != 4:
						print("multiSet neopixel mqtt issue with pipe in: '%s'" % str(dIn))
						#We might want to send a message back reporting the failure.
						continue
					
					if "data" not in dIn:
						print("multiSet neopixel mqtt issue with pipe in [no data]")
						#We might want to send a message back reporting the failure.
						continue

					for key in dIn["data"]["leds"]: #We're only doing this for the future possibility of multiple led's set in one command
						setDictI["data"]["leds"][key] = dIn["data"]["leds"][key]

		if DEBUG:
			print("MultiSet acquiring semaphores.")

		self.threadPostSema.acquire() #We want blocking from this direction.

		if DEBUG == 2:
			print("multiset data pushing out:")
			pprint.pprint(setDictI)

		try:
			#self.threadSema.acquire()

			if DEBUG:
				print("MultiSet acquired threadSema.")
			
			#Send message
			if setDictI['type'] == "neopixel":
				try:
					if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(setDictI)):
						print("multiSet neopixel mqtt issue sending message.")
				except:
					print("multiSet neopixel mqtt, exception met when sending message.")

			#self.threadSema.release()
			if DEBUG:
				print("MultiSet released threadSema.")
		except:
			#self.threadSema.release()
			self.threadPostSema.release()
			if DEBUG:
				print("Multiset returning bad.")
			return 1

		self.threadPostSema.release()

		if DEBUG:
			print("MultiSet returning good.")
		return 0


	#Once every 10 seconds we want to make a publish call which posts all known data
	#Once every minute, each class instance type provided will get called for management
	# information in order to make sure everything is updated (Without constantly making
	# calls which have no need getting called a billion times a second)
	def publisher(self):
		cfgData = {}

		if DEBUG:
			print("mqtt publisher called.")

		#self.client.publish("/%s" % str(self.hostname), str(SERVICEID))

		for device in self.devices:
			if "mhconfig" not in self.devices[device]: #This shouldn't be possible.
				print("UART_MH_MQTT.publisher(), no mhconfig")
				continue

			if DEBUG == 1:
				print("publishing devices.")
			self.client.publish("/%s/uartmh" % str(self.hostname), str(device))

			cfgData[device] = {}
			
			#Aggregate each mh instance management data.
			if "neopixel" in self.devices[device]:
				cfgData[device]["neopixel"] = []
		
				#data = self.messageHandlers["neopixel"].np_manage()
				data = self.devices[device]["neopixel"].np_manage()

				if DEBUG:
					print("np manage out:")
					pprint.pprint(data)

				try:
				# if True:
					if not data.startswith("NAK"):
						datal = list(data)
						if DEBUG:
							print("datal prep:")
							pprint.pprint(datal)

						count = struct.unpack("<B", datal.pop(0))[0]

						if DEBUG:
							print("Count is: %s" % str(count))
							print("datal postp:")
							pprint.pprint(datal)

						for i in range(0, count):
							relI = i * 4
							if DEBUG:
								print("relI is: %s, i is: %s" % (str(relI), str(i)))
							#pID = struct.unpack(">B", data[0+relI])[0]
							pID = struct.unpack(">B", data[1+relI])[0]
							#pin = struct.unpack(">B", data[1+relI])[0]
							pin = struct.unpack(">B", data[2+relI])[0]
							#length = struct.unpack(">H", datal[2+relI:4+relI])[0]
							length = struct.unpack(">H", data[3+relI:5+relI])[0]
							if DEBUG:
								print("publisher neopixel data: %s,%s,%s" % ( str(pID), str(pin), str(length) ) )
							cfgData[device]["neopixel"].append({ "id":pID, "pin":pin, "length":length })
				except:
				# else:
					if DEBUG:
						print("Malformed np_manage data.")
			if "digital" in self.devices[device]:
				cfgData[device]["digital"] = []

				data = self.devices[device]["digital"].digi_manage()

				if DEBUG:
					print("digi manage out:")
					pprint.pprint(data)

				try:
					if not data.startswith("NAK"):
						datal = list(data)

						if DEBUG:
							print("digi datal prep:")
							pprint.pprint(datal)

						count = struct.unpack("<B", datal.pop(0))[0] #Get the first byte

						for i in range(0, count):
							relI = i * 6
							if DEBUG:
								print("relI is: %s, i is: %s" % (str(relI), str(i)))
								
							pin = struct.unpack("<h", data[1+relI:3+relI])[0]
							direction = struct.unpack("<B", data[3+relI])[0]
							state = struct.unpack("<h", data[4+relI:6+relI])[0]
							pClass = struct.unpack("<B", data[6+relI])[0]

							if DEBUG:
								print("publisher digital data: %s, %s, %s, %s" % ( str(pin), str(direction), str(state), str(pClass) ) )

							lPin = { "pin":pin, "direction":direction, "state":state, "class":pClass }
							self.devices[device]["digital"].addPin(copy.copy(lPin))
							cfgData[device]["digital"].append( lPin )
				except:
					if DEBUG:
						print("Malformed digi_manage data.")
# data.data = in->pin;
# _uart->write(data.raw, 2); // pin
# _uart->write(in->dir); // dir
# data.data = in->state;
# _uart->write(data.raw, 2); //state
# _uart->write(in->pClass); //pclass




		if DEBUG == 2:
			print("Config data:")
			pprint.pprint(cfgData)

			#if "digital" in self.messageHandlers
		for device in cfgData:
			ltopic = "/%s/%s/%s" % ( str(self.hostname), str(SERVICEID), str(device) )

			for mhType in cfgData[device]:
				if mhType == "neopixel":
					#Publish configuration data
					for data in cfgData[device]["neopixel"]:
						#Make sure each dict value contains id,pin and length.
						self.client.publish("%s/neopixel/%s/config" % ( str(ltopic), str(data["id"]) ),"o")
						self.client.publish("%s/neopixel/%s/config/pin" % ( str(ltopic), str(data["id"]) ),str(data["pin"]))
						self.client.publish("%s/neopixel/%s/config/length" % ( str(ltopic), str(data["id"]) ),str(data["length"]))

				if mhType == "digital":
					for data in cfgData[device]["digital"]:
						self.client.publish("%s/digital/%s/config" % ( str(ltopic), str(data["pin"]) ), "o")
						self.client.publish("%s/digital/%s/config/direction" % ( str(ltopic), str(data["pin"]) ), str(data["direction"]))
						self.client.publish("%s/digital/%s/config/class" % ( str(ltopic), str(data["pin"]) ), str(data["class"]))
						self.client.publish("%s/digital/%s/config/state" % ( str(ltopic), str(data["pin"]) ), str(data["state"]))
					#Publish pin data (Not yet implemented in fw)
					#for data in pinData:
					#	self.client.publish("/%s/neopixel/%s/config/leds" % ( str(self.hostname),str(data["id"]) ),"o")
					#	for leds in data["leds"]:
					#	self.client.publish("/%s/neopixel/%s/config/leds" % ( str(self.hostname),str(data["id"]),str(leds[0]) ), str(leds[1])) #where leds[0] is the pixel, and leds[1] is the csv rgb value

	def run(self):
		#Start thread for message/connection handling.
		self.client.loop_start()

		# Here, we call the method to populate this unique arduino device's ID
		#self.getFirmwareName()

		#  This is the counter value for the modulus statements.
		bigCounter = 0

		#  These are modulus values for calling a separate publisher which
		# queries the pin and pixel states via a call to to the GET sub-
		# -command.
		pixelInfoMod = 4
		digitalInfoMod = 4

		while True:
			#  This is the most common publisher statement, it shows basic
			# configuration stuff and locally saved data.
			self.publisher()
			bigCounter += 1

			#This queries all of the neopixel strands for color and pin data. (active)
			if (bigCounter % pixelInfoMod) == 0:
				#self.getSettings("neopixel") # This method will save the data to class and perform the publishing.
				pass

			#This queries the digital instance data for pin mode
			if (bigCounter % digitalInfoMod) == 0:
				#self.getSettings("digital")
				pass

			if bigCounter >= 65535: #Lets stop at a big-ish number.
				bigCounter = 0

			time.sleep(10)