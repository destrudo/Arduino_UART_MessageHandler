#include <Arduino.h>
#include <USBAPI.h>
#include "UART-BaseC.h"


BaseSerial_::BaseSerial_()
{
	_type = SERIAL_NOTYPE;
}

#if defined(USBCON)
BaseSerial_::BaseSerial_(Serial_ * ser)
{
	_type = SERIAL_USBCDM;
	usb_ser = ser;
}
#endif

BaseSerial_::BaseSerial_(HardwareSerial * ser)
{
	_type = SERIAL_HWSER;
	hw_ser = ser;
}

void BaseSerial_::begin(unsigned long baud)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->begin(baud);
		#endif

		case SERIAL_HWSER:
			return hw_ser->begin(baud);
	}
}

void BaseSerial_::end(void)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->end();
		#endif

		case SERIAL_HWSER:
			return hw_ser->end();
	}
}

int BaseSerial_::available(void)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->available();
		#endif

		case SERIAL_HWSER:
			return hw_ser->available();
	}

	return 0;
}

int BaseSerial_::peek(void)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->peek();
		#endif

		case SERIAL_HWSER:
			return hw_ser->peek();
	}
	return 0;
}

int BaseSerial_::read(void)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->read();
		#endif

		case SERIAL_HWSER:
			return hw_ser->read();
	}
	return 0;
}

void BaseSerial_::flush(void)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->flush();
		#endif

		case SERIAL_HWSER:
			return hw_ser->flush();
	}
}

size_t BaseSerial_::write(uint8_t data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->write(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->write(data);
	}
	return 0;
}

size_t BaseSerial_::write(const uint8_t * data, size_t size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->write(data,size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->write(data,size);
	}
	return 0;
}

size_t BaseSerial_::readBytes(uint8_t * data, size_t size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->readBytes(data,size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->readBytes(data,size);
	}
	return 0;
}

size_t BaseSerial_::readBytes(char * data, size_t size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->readBytes(data,size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->readBytes(data,size);
	}
	return 0;
}

void BaseSerial_::setTimeout(unsigned long data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->setTimeout(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->setTimeout(data);
	}
}


size_t BaseSerial_::print(const __FlashStringHelper * data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data);
	}
	return 0;
}

size_t BaseSerial_::print(const String & data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data);
	}
	return 0;
}

size_t BaseSerial_::print(const char data[])
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data);
	}
	return 0;
}

size_t BaseSerial_::print(char data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data);
	}
	return 0;
}
size_t BaseSerial_::print(unsigned char data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data, size);
	}
	return 0;
}
size_t BaseSerial_::print(int data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data, size);
	}
	return 0;
}
size_t BaseSerial_::print(unsigned int data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data, size);
	}
	return 0;
}
size_t BaseSerial_::print(long data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data, size);
	}
	return 0;
}
size_t BaseSerial_::print(unsigned long data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data, size);
	}
	return 0;
}
size_t BaseSerial_::print(double data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data, size);
	}
	return 0;
}
size_t BaseSerial_::print(const Printable& data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->print(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->print(data);
	}
	return 0;
}




size_t BaseSerial_::println(const __FlashStringHelper * data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data);
	}
	return 0;
}

size_t BaseSerial_::println(const String &data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data);
	}
	return 0;
}

size_t BaseSerial_::println(const char data[])
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data);
	}
	return 0;
}
size_t BaseSerial_::println(char data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data);
	}
	return 0;
}
size_t BaseSerial_::println(unsigned char data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data, size);
	}
	return 0;
}
size_t BaseSerial_::println(int data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data, size);
	}
	return 0;
}
size_t BaseSerial_::println(unsigned int data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data, size);
	}
	return 0;
}
size_t BaseSerial_::println(long data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data, size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data, size);
	}
	return 0;
}
size_t BaseSerial_::println(unsigned long data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data,size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data,size);
	}
	return 0;
}
size_t BaseSerial_::println(double data, int size)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data,size);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data,size);
	}
	return 0;
}
size_t BaseSerial_::println(const Printable& data)
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println(data);
		#endif

		case SERIAL_HWSER:
			return hw_ser->println(data);
	}
	return 0;
}

size_t BaseSerial_::println()
{
	switch (_type) {
		#if defined(USBCON)
		case SERIAL_USBCDM:
			return usb_ser->println();
		#endif

		case SERIAL_HWSER:
			return hw_ser->println();
	}
	return 0;
}