/*
 * UART-BaseC.h, header for UART-BaseC
 *
 * This is a library for uniting all of the serial types so that class instance
 * vars don't need to be different for HardwareSerial/Serial_/SoftwareSerial.
 */

#ifndef UART_BASE_C
#define UART_BASE_C

#include <Arduino.h>
#include <USBAPI.h>

#define SERIAL_NOTYPE -1
#define SERIAL_USBCDM 0
#define SERIAL_HWSER 1
#define SERIAL_SWSER 2

class BaseSerial_
{
private:
	#if defined(USBCON)
	Serial_ * usb_ser;
	#endif
	HardwareSerial * hw_ser;
	// SoftwareSerial * sw_ser;

	short int _type;
	
public:
	BaseSerial_();
	#if defined(USBCON)
	BaseSerial_(Serial_ *);
	#endif
	BaseSerial_(HardwareSerial *);
	// BaseSerial_(SoftwareSerial *);

	void begin(unsigned long);
	// void begin(unsigned long, uint8_t);
	void end(void);

	short int getType(void) { return _type; }

	int available(void);
	int peek(void);
	int read(void);

	size_t print(const __FlashStringHelper *);
    size_t print(const String &);
    size_t print(const char[]);
    size_t print(char);
    size_t print(unsigned char, int = DEC);
    size_t print(int, int = DEC);
    size_t print(unsigned int, int = DEC);
    size_t print(long, int = DEC);
    size_t print(unsigned long, int = DEC);
    size_t print(double, int = 2);
    size_t print(const Printable&);

    size_t println(const __FlashStringHelper *);
    size_t println(const String &s);
    size_t println(const char[]);
    size_t println(char);
    size_t println(unsigned char, int = DEC);
    size_t println(int, int = DEC);
    size_t println(unsigned int, int = DEC);
    size_t println(long, int = DEC);
    size_t println(unsigned long, int = DEC);
    size_t println(double, int = 2);
    size_t println(const Printable&);
    size_t println(void);

	size_t readBytes(uint8_t *, size_t);
	size_t readBytes(char *, size_t);
	void setTimeout(unsigned long);



	void flush(void);

	size_t write(uint8_t);
	size_t write(const uint8_t *, size_t);
	operator bool() { return true; }


};

#endif /* UART_BASE_C */