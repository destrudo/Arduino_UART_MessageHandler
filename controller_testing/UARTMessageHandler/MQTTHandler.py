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

		#for neopixel
		if "neopixel" in msg.topic and "neopixel" in self.devices[msgIdent]:
			if DEBUG:
				print("neopixel mqtt message.")
			msgL = msg.topic.split("/")

			if len(msgL) < 5:
				print("Bogus neopixel message received. [incomplete data]")
				return None

			#Make sure that we've gotten a sane response.
			if isInt(msgL[5]):
				if (int(msgL[5]) > 254) or (int(msgL[5]) < 0):
					print("Bogus neopixel message received. [strand id error]")
					return None
			else:
				#if (msgL[3] != "add") and (msgL[3] != "del") and (msgL[3] != "clear"):
				if (msgL[5] != "add"):
					print("Bogus neopixel message received. [unexpected topic '%s']" % str(msgL[4]))
					return None

			#This is the only instance where a strand ID is not specified (Since it won't exist until this is called)
			if msgL[5] == "add":
				if DEBUG:
					print("neopixel mqtt message [add]")

				#We actually want this to generate a dict which contains:
				# { 'id'=id, "command":"add", "type":"neopixel", "data":{"pin":pin, "length":len} }
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


				#self.threadSema.acquire()
				if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(umhmsg)):
					print("neopixel mqtt issue sending message.")
				#self.threadSema.release()

				return None #After this we want to leave.

			#If we have one of the initiation commands
			if len(msgL) >= 6:
				if msgL[6] == "set" or msgL[6] == "seti": #Set commands handler
					if DEBUG:
						print("### set command called. (%s)" % str(msgL[5]))
					rgbS = msg.payload.split(",")
					rgbI = []
					for sv in rgbS:
						rgbI.append(int(sv))

					for iChk in rgbS:
						if iChk == "" or iChk == None: #If we have a blank message.
							print("neopixel mqtt blank message.")
							return None

						if int(iChk) < 0 or int(iChk) >= 255:
							print("neopixel mqtt message outside int limits.")
							return None

					umhmsg = {
						"id":int(msgL[5]),
						"command":"ctrl",
						"type":"neopixel",
						"data":{
							"leds":{ str(msgL[7]):rgbI }
						}
					}

					print("umhmsg: ")
					pprint.pprint(umhmsg)

					if msgL[6] == "seti":
						print("Seti!")
						umhmsg["command"] = "ctrli"
						#self.threadSema.acquire()
						if DEBUG:
							print("neopixel mqtt seti acquired threadSema.")

						print("seti data to send:")
						pprint.pprint(umhmsg)

						if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(umhmsg)):
							print("neopixel mqtt seti issue sending message.")

						#self.threadSema.release()
						if VERBOSE:
							print("UART_MH_MQTT.on_message() complete (seti).")
						return None


					if DEBUG:
						print("umhmsg output data:")
						pprint.pprint(umhmsg)


					if int(msgL[5]) not in self.threadInstances:
						#Cool, create a fresh new one and fresh new pipes and start it.
						self.threadInstancePipes[int(msgL[5])] = multiprocessing.Pipe()
						#If we have data in the busyThreadBuffer, we want to apply it to umhmsg
						if int(msgL[5]) in self.busyThreadBuffer:
							if DEBUG:
								print("Data in BUSYTHREADBUFFER")
							if len(self.busyThreadBuffer[msgL[5]]) > 0:
								for data in self.busyThreadBuffer[msgL[5]]:
									for part in data['data']:
										umhmsg['data'][part] = data['data'][part]

							self.busyThreadBuffer.pop(int(msgL[5]), None)

							if DEBUG:
								print("Cleared BUSYTHREADBUFFER")
								
						self.threadInstances[int(msgL[5])] = multiprocessing.Process(target=self.multiSet, args=(umhmsg, self.threadInstancePipes[int(msgL[5])], copy.copy(msgIdent), MQTTPROCESSTIMEOUT, MQTTPROCESSTIMELIMIT,))
						self.threadInstances[int(msgL[5])].start()
						if DEBUG:
							print("### msgL[3]: %s not in threadInstances." % str(msgL[4]))
						return None #Break out completely, we don't want to do anything else.

					#Call a join
					try:
						self.threadInstances[int(msgL[5])].join(0.005)
					except:
						if DEBUG:
							print("### ThreadInstances join error")
							return None

					if self.threadInstances[int(msgL[5])].is_alive(): #If it's been started.
					####RECENT MODS
						if not self.threadPostSema.acquire(False): #If threadPostSema is currently blocking
							if not int(msgL[5]) in self.busyThreadBuffer:
								self.busyThreadBuffer[int(msgL[5])] = []

							self.busyThreadBuffer[int(msgL[5])].append(copy.copy(umhmsg))

							if DEBUG:
								print("BUSYTHREADBUFFER ADDED A MESSAGE WHEN SEMA ACQUISITION FAILED!")
						else:

							#we want to pass the umhmsg in.
							self.threadInstancePipes[int(msgL[5])][1].send(umhmsg)

						self.threadPostSema.release() #Release no matter what.
					else:
						#I probably need not call these.
						#self.threadInstancePipes[int(msgL[3])][0].close()
						#self.threadInstancePipes[int(msgL[3])][1].close()
						self.threadInstancePipes[int(msgL[5])] = None
						#Thread cleanup ?
						self.threadInstances[int(msgL[5])].terminate()
						self.threadInstances[int(msgL[5])] = None

						self.threadInstancePipes[int(msgL[5])] = multiprocessing.Pipe()
						self.threadInstances[int(msgL[5])] = multiprocessing.Process(target=self.multiSet, args=(umhmsg, self.threadInstancePipes[int(msgL[5])], msgIdent, MQTTPROCESSTIMEOUT, MQTTPROCESSTIMELIMIT,))
						self.threadInstances[int(msgL[5])].start()

				elif msgL[6] == "del": #deletion command
					#Make sure that the message value is the ID
					if msg.payload != msgL[5]:
						print("neopixel mqtt del command issued with mismatched payload. [%s,%s]" % ( str(msgL[5]), str(msg.payload) ) )
					#Create the message
					umhmsg = {
						"id":int(msgL[5]),
						"command":"del",
						"type":"neopixel",
						"data":{
							"id":int(msg.payload) #I could just use msgL[3], but it seems more useful.
						}
					}

					#self.threadSema.acquire()
					if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(umhmsg)):
						print("neopixel mqtt issue sending del message.")
					#self.threadSema.release()

				elif msgL[6] == "clear":
					#Make sure that the message values is the ID
					if msg.payload != msgL[5]:
						print("neopixel mqtt clear command issued with mismatched payload. [%s,%s]" % ( str(msgL[5]), str(msg.payload) ) )
					
					#create the message
					umhmsg = {
						"id":int(msgL[5]),
						"command":"clear",
						"type":"neopixel",
						"data":{
							"id":int(msg.payload) #I could just use msgL[3], but it seems more useful.
						}
					}

					print("mqtt np clear message:")
					pprint.pprint(umhmsg)
					#send it
					#self.threadSema.acquire()
					if self.devices[msgIdent]["neopixel"].sendMessage(self.devices[msgIdent]["neopixel"].createMessage(umhmsg)):
						print("neopixel mqtt issue sending clear message.")

					#self.threadSema.release()

		#for digital
		if VERBOSE:
			print("UART_MH_MQTT.on_message() complete.")

	#This is for set commands which support more than one command at the same time (Thus the need to concat a bunch of commands together.)
	def multiSet(self, setDictI, pipeD, msgIdent, timeout, timeLimit):
		cTimeout = time.time() + timeout
		cTimeLimit = time.time() + timeLimit
		print("multiSet message ident: %s" % str(msgIdent))

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

			print("publishing devices.")
			self.client.publish("/%s/uartmh" % str(self.hostname), str(device))

			cfgData[device] = {}
			
			#Aggregate each mh instance management data.
			if "neopixel" in self.devices[device]:
				cfgData[device]["neopixel"] = []
		
				#data = self.messageHandlers["neopixel"].np_manage()
				data = self.devices[device]["neopixel"].np_manage()
		
				if DEBUG:
					print("PUBLISHER 00 RELEASE SEMAPHORE")
		
				#self.threadSema.release()

				if DEBUG:
					print("np manage out:")
					pprint.pprint(data)

				#try:
				if True:
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
				#except:
				else:
					if DEBUG:
						print("Malformed np_manage data.")

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
		pixelInfoMod = 7
		digitalInfoMod = 6

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