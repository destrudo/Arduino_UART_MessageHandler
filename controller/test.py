#!/usr/bin/python

import serial
import time
import binascii
import itertools
import sys

def lrcsum(dataIn):
	lrc = 0
	for b in dataIn:
		lrc ^= b
	return lrc

		#key
			#cmd
				#scmd
					#version
						#out
							#in
buf = []
buf.append(0xaa) #key
buf.append(0x02) #cmd 0
buf.append(0x00) #cmd 1
buf.append(0xfe) #scmd
buf.append(0x00) #version
buf.append(0x01) #out 0
buf.append(0x00) #out 1
buf.append(0x00) #in 0
buf.append(0x00) #in 1
buf.append(lrcsum(buf))
#These are NP-specific
buf.append(0x01) #id
buf.append(0x06) #pin
buf.append(0x65) #length 0
buf.append(0x00) #length 1
print buf


lSer = serial.Serial("/dev/ttyUSB0", 250000)

# lSer.write(chr(0x00))
# lSer.write(chr(0x00))
# lSer.write(chr(0x00))

for b in buf:
	try:
	#	bl = []
	#	bl.append(b)
		lSer.write(chr(b))
	except:
		print "Failed to write char"
		pass

time.sleep(1)

buf = None
buf = []
buf.append(0xaa) #key
buf.append(0x02) #cmd 0
buf.append(0x00) #cmd 1
buf.append(0x01) #scmd
buf.append(0x00) #version
buf.append(0x01) #out 0
buf.append(0x00) #out 1
buf.append(0x00) #in 0
buf.append(0x00) #in 1
buf.append(lrcsum(buf))
#These are NP-specific
buf.append(0x01) #id
buf.append(0x00) #pixel 0
buf.append(0x00) #pixel 1
buf.append(0xff) #red
buf.append(0xff) #green
buf.append(0xff) #blue
print buf

# lSer.write(chr(0x00))
# lSer.write(chr(0x00))
# lSer.write(chr(0x00))

for b in buf:
	try:
	#	bl = []
	#	bl.append(b)
		lSer.write(chr(b))
	except:
		print "Failed to write char"
		pass


time.sleep(1)


buf = None
buf = []
buf.append(0xaa) #key
buf.append(0x02) #cmd 0
buf.append(0x00) #cmd 1
buf.append(0x02) #scmd
buf.append(0x00) #version
buf.append(0x01) #out 0
buf.append(0x00) #out 1
buf.append(0x00) #in 0
buf.append(0x00) #in 1
buf.append(lrcsum(buf))
#These are NP-specific
buf.append(0x01) #id

print buf

# lSer.write(chr(0x00))
# lSer.write(chr(0x00))
# lSer.write(chr(0x00))

for b in buf:
	try:
	#	bl = []
	#	bl.append(b)
		lSer.write(chr(b))
	except:
		print "Failed to write char"
		pass

#add 101 length strip on pin 6
#bufa = b'\xaa\x00\x02\xfe\x00\x00\x01\x00\x00\x57\x01\x06\x00\x65'
#lSer.write(bufa)

# time.sleep(1)

#add 4 length strip on pin 9
# buf = b'\x01\xaa\x01\x09\x00\x04\x55'
# lSer.write(buf)

# time.sleep(1)

#Clear strip 0
# buf = b'\x03\xaa\x00\x55'
# lSer.write(buf)

# time.sleep(1)

#Clear strip 1
# buf = b'\x03\xaa\x01\x55'
# lSer.write(buf)

# time.sleep(1)

# buf = b'\x02\xaa\x00\x00\x55'
# lSer.write(buf)

# lSer.close()

# sys.exit(9)


# val = 0

# for i in itertools.product(list(range(0,254)), list(range(0,254)), list(range(0,254))):
# 	try:
# 		lSer.open()
# 	except:
# 		pass

# 	lData = [ 0x00, 0xaa, 0x00, 0x00, 0x01, 0x00, val, i[0], i[1], i[2], 0x55 ]
# 	for b in lData:
# 		try:
# 			lSer.write(chr(b))
# 		except:
# 			pass

# 	time.sleep(0.15)

# 	lData = [ 0x00, 0xaa, 0x01, 0x00, 0x01, 0x00, val % 4, i[0], i[1], i[2], 0x55 ]
# 	for b in lData:
# 		try:
# 			lSer.write(chr(b))
# 		except:
# 			pass

# 	time.sleep(0.15)

# 	val+=1

# 	if val >= 101:
# 		val = 0

# 	try:
# 		lSer.close()
# 	except:
# 		pass

lSer.close()
