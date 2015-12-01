###############################################################################
#                                MQTTHandler.py                               #
#                                                                             #
# Python library for controlling an arduino using Arduino_UART_MessageHandler #
#  utilizing an mqtt client.                                                  #
#                                                                             #
###############################################################################
from __future__ import print_function

import serial
import pprint
import sys
import struct
import time
import socket

#Separating this because when I move the module out it'll be happier.
import paho.mqtt.client as mqtt
import multiprocessing

from UARTMessageHandler import *
#from UARTMessageHandler import UART_MH
from UARTConfig import *
from UARTDigital import *
from UARTNeopixel import *

DEBUG = 0

#Device class ID (For device differentiation)
SERVICEID="uartmh"

#Separating this because when I move the module out it'll be happier.
MQTTPROCESSTIMEOUT = 5
MQTTPROCESSTIMELIMIT = 60

#This will be the class to handle mqtt messages
class UART_MH_MQTT:
	def __init__(self,hostname,port):
		self.hostname = str(socket.gethostname())
		self.client = mqtt.Client(client_id="uart-mh@%s" % self.hostname)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(hostname, port, 10)
		self.messageHandlers = {}

		self.neopixelBuffer = {}
		self.timeElapsed = 0
		self.timeMax = 200 #(ms)

		self.threadInstances = {}
		self.threadInstancePipes = {}

		self.threadSema = multiprocessing.Semaphore()

	def has_instance(self, name):
		if len(self.messageHandlers) == 0:
			return False

		if str(name) not in self.messageHandlers:
			return False

		return True

	def add_instance(self, name, instance):
		self.messageHandlers[name] = instance

	def on_connect(self, client, userdata, flags, rc):
		self.client.subscribe("/%s/#" % self.hostname, 2)
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

	#This is the worker thread to be which waits for timeMax or a send command to be reached
	def neopixel_set_t(self):
		#Get current time
		#if (current time) == (lastTime + timeMax):
		#	send data
		pass

	def on_message(self, client, userdata, msg):
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

		#for neopixel
		if msg.topic.startswith("/%s/neopixel" % str(self.hostname)) and self.has_instance("neopixel"): #and we have a neopixel instance created.
			if DEBUG:
				print("neopixel mqtt message.")
			msgL = msg.topic.split("/")

			if len(msgL) < 3:
				print("Bogus neopixel message received. [incomplete data]")
				return None

			#Make sure that we've gotten a sane response.
			if isInt(msgL[3]):
				if (int(msgL[3]) > 254) or (int(msgL[3]) < 0):
					print("Bogus neopixel message received. [strand id error]")
					return None
			else:
				#if (msgL[3] != "add") and (msgL[3] != "del") and (msgL[3] != "clear"):
				if (msgL[3] != "add"):
					print("Bogus neopixel message received. [unexpected topic '%s']" % str(msgL[3]))
					return None

			#This is the only instance where a strand ID is not specified (Since it won't exist until this is called)
			if msgL[3] == "add":
				if DEBUG:
					print("neopixel mqtt message [add]")

				#We actually want this to generate a dict which contains:
				# { 'id'=id, "command":"add", "type":"neopixel", "data":{"pin":pin, "length":len} }
				data = msg.payload.split(",")

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


				self.threadSema.acquire()
				if self.messageHandlers["neopixel"].sendMessage(self.messageHandlers["neopixel"].createMessage(umhmsg)):
					print("neopixel mqtt issue sending message.")
				self.threadSema.release()

				return None #After this we want to leave.

			#If we have one of the initiation commands
			if len(msgL) >= 4:
				if msgL[4] == "set": #Set command handler
					if DEBUG:
						print("### set command called.")
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
						"id":int(msgL[3]),
						"command":"ctrl",
						"type":"neopixel",
						"data":{
							"leds":{ str(msgL[5]):rgbI }
						}
					}


					if int(msgL[3]) not in self.threadInstances:
						#Cool, create a fresh new one and fresh new pipes and start it.
						self.threadInstancePipes[int(msgL[3])] = multiprocessing.Pipe()
						self.threadInstances[int(msgL[3])] = multiprocessing.Process(target=self.multiSet, args=(umhmsg, self.threadInstancePipes[int(msgL[3])], MQTTPROCESSTIMEOUT, MQTTPROCESSTIMELIMIT,))
						self.threadInstances[int(msgL[3])].start()
						if DEBUG:
							print("### msgL[3]: %s not in threadInstances." % str(msgL[3]))
						return None #Break out completely, we don't want to do anything else.

					#Call a join
					try:
						self.threadInstances[int(msgL[3])].join(0.25)
					except:
						if DEBUG:
							print("### ThreadInstances join error")
							return None

					if self.threadInstances[int(msgL[3])].is_alive(): #If it's been started.
						#If it's alive, we want to pass the umhmsg in.
						self.threadInstancePipes[int(msgL[3])][1].send(umhmsg)
					else:
						#I probably need not call these.
						#self.threadInstancePipes[int(msgL[3])][0].close()
						#self.threadInstancePipes[int(msgL[3])][1].close()
						self.threadInstancePipes[int(msgL[3])] = None
						#Thread cleanup ?
						self.threadInstances[int(msgL[3])].terminate()
						self.threadInstances[int(msgL[3])] = None

						self.threadInstancePipes[int(msgL[3])] = multiprocessing.Pipe()
						self.threadInstances[int(msgL[3])] = multiprocessing.Process(target=self.multiSet, args=(umhmsg, self.threadInstancePipes[int(msgL[3])], MQTTPROCESSTIMEOUT, MQTTPROCESSTIMELIMIT,))
						self.threadInstances[int(msgL[3])].start()

				elif msgL[4] == "del": #deletion command
					#Make sure that the message value is the ID
					if msg.payload != msgL[3]:
						print("neopixel mqtt del command issued with mismatched payload. [%s,%s]" % ( str(msgL[3]), str(msg.payload) ) )
					#Create the message
					umhmsg = {
						"id":int(msgL[3]),
						"command":"del",
						"type":"neopixel",
						"data":{
							"id":int(msg.payload) #I could just use msgL[3], but it seems more useful.
						}
					}

					self.threadSema.acquire()
					if self.messageHandlers["neopixel"].sendMessage(self.messageHandlers["neopixel"].createMessage(umhmsg)):
						print("neopixel mqtt issue sending del message.")
					self.threadSema.release()

				elif msgL[4] == "clear":
					#Make sure that the message values is the ID
					if msg.payload != msgL[3]:
						print("neopixel mqtt clear command issued with mismatched payload. [%s,%s]" % ( str(msgL[3]), str(msg.payload) ) )
					
					#create the message
					umhmsg = {
						"id":int(msgL[3]),
						"command":"clear",
						"type":"neopixel",
						"data":{
							"id":int(msg.payload) #I could just use msgL[3], but it seems more useful.
						}
					}

					#send it
					self.threadSema.acquire()
					if self.messageHandlers["neopixel"].sendMessage(self.messageHandlers["neopixel"].createMessage(umhmsg)):
						print("neopixel mqtt issue sending clear message.")

					self.threadSema.release()

		#for digital

	#This is for set commands which support more than one command at the same time (Thus the need to concat a bunch of commands together.)
	def multiSet(self, setDictI, pipeD, timeout, timeLimit):
		cTimeout = time.time() + timeout
		cTimeLimit = time.time() + timeLimit
		if DEBUG:
			print("### MULTISET ENTERED WITH setDictI: %s" % str(setDictI))
		while ( (time.time() < cTimeout) and time.time() < cTimeLimit and pipeD != None ):
			if pipeD[0].poll(1): #We'll poll for a second (Since it has little bearing on the world)
				dIn = pipeD[0].recv()
				if DEBUG:
					print("### multiSet got message in pipe: %s" % str(dIn))

				if isinstance(dIn, str): #If we have one of the request inputs [NI]
					#Do things for single string
					continue

				if not isinstance(dIn, dict):
					print("### multiSet didn't get dict post string check.")
					continue

				if setDictI['type'] == "neopixel":
					#Do neopixel verification stuff
					#We should have gotten a single value dict:
					#	PIN:"RED,GREEN,BLUE"
					#Make sure pin is within 0 and len-1
					#Make sure each RGB value is between 0 and 255
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
					
#		print("multiSet bailing with dict data:\n#########################")
#		pprint.pprint(setDictI)
#		print("#########################")
		try:
			self.threadSema.acquire()
			#Send message
			if setDictI['type'] == "neopixel":
				if self.messageHandlers["neopixel"].sendMessage(self.messageHandlers["neopixel"].createMessage(setDictI)):
					print("multiSet neopixel mqtt issue sending message.")


			self.threadSema.release()
		except:
			return 1
		return 0


	#Once every 10 seconds we want to make a publish call which posts all known data
	#Once every minute, each class instance type provided will get called for management
	# information in order to make sure everything is updated (Without constantly making
	# calls which have no need getting called a billion times a second)
	def publisher(self):
		cfgData = {}

		self.client.publish("/%s" % str(self.hostname), str(SERVICEID))

		#Aggregate each mh instance management data.
		if "neopixel" in self.messageHandlers:
			cfgData["neopixel"] = []

			self.threadSema.acquire()
			data = self.messageHandlers["neopixel"].np_manage()
			self.threadSema.release()

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
						cfgData["neopixel"].append({ "id":pID, "pin":pin, "length":length })
			#except:
			else:
				if DEBUG:
					print("Malformed np_manage data.")

		#if "digital" in self.messageHandlers

		for mhType in cfgData:
			if mhType == "neopixel":
				#Publish configuration data
				for data in cfgData["neopixel"]:
					#Make sure each dict value contains id,pin and length.
					self.client.publish("/%s/neopixel/%s/config" % ( str(self.hostname),str(data["id"]) ),"o")
					self.client.publish("/%s/neopixel/%s/config/pin" % ( str(self.hostname),str(data["id"]) ),str(data["pin"]))
					self.client.publish("/%s/neopixel/%s/config/length" % ( str(self.hostname),str(data["id"]) ),str(data["length"]))

				#Publish pin data (Not yet implemented in fw)
				#for data in pinData:
				#	self.client.publish("/%s/neopixel/%s/config/leds" % ( str(self.hostname),str(data["id"]) ),"o")
				#	for leds in data["leds"]:
				#	self.client.publish("/%s/neopixel/%s/config/leds" % ( str(self.hostname),str(data["id"]),str(leds[0]) ), str(leds[1])) #where leds[0] is the pixel, and leds[1] is the csv rgb value

	def run(self):
		#Start thread for message/connection handling.
		self.client.loop_start();

		while True:
			self.publisher()
			time.sleep(10)