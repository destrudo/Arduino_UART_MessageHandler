/*
 * UART-MessageHandler.h, header for UART-MessageHandler
 *
 * UART-MessageHandler is a library for a protocol on top of UART for
 *  controlling various arduino-related instances.  Each message is (poorly)
 *  checksummed and contains message length data as well as expected return
 *  data lengths.
 */

#ifndef UART_MESSAGEHANDLER_H
#define UART_MESSAGEHANDLER_H

#include <Arduino.h>
#include "UART_Digital.h"
#include "UART_Neopixel.h"

#define UART_MH_HEADER_SIZE 10
#define UART_MH_HEADER_KEY 0xAA

#define UART_MH_MAX_MSG_SIZE 256

#define CMD_UART_MESSAGEHANDLER 0x00
#define CMD_UART_DIGITAL 0x01
#define CMD_UART_NEOPIXEL 0x02

//#define DEBUG

/* lrc checksum */
uint8_t lrcsum(uint8_t * data, uint8_t datasz);

struct UART_Header_s
{
	uint8_t key;
	uint16_t cmd;
	uint8_t scmd;
	uint8_t version;
	uint16_t out;
	uint16_t in;
	uint8_t chksum;
};

union UART_Header
{
	uint8_t raw[UART_MH_HEADER_SIZE];
	UART_Header_s data;
};

class UART_MessageHandler
{
 private:
 	HardwareSerial * _uart;
 	uint8_t * _buf;

/* I don't want to do this via preprocessor, but it doesn't really matter */
//#ifdef USE_UART_NEOPIXEL /* Add the instance for the uart neopixel */
 	UART_Neopixel * _neopixel;
// #else //This is a fucking HORRIBLE hack.
 	// uint8_t * _neopixel;
// #endif

//#ifdef UART_DIGITAL_H /* Add the instance for the uart digital */
 	UART_Digital * _digital;
//#else
// 	uint8_t * _digital;
//#endif

 public:
 	UART_MessageHandler();
 	UART_MessageHandler(HardwareSerial * uart, uint16_t baud);

 	void setUART(HardwareSerial * uart);
 	void begin(uint16_t baud);

 	/* uint8_t checkHeader(UART_Header_s * header); */

 	uint8_t handleMsg(uint16_t len);
 	uint16_t readMsg();
 	uint8_t * getBuf();

 	uint16_t run(uint8_t * status);
 	void clear();

/* Object-specific calls. */
// #ifdef USE_UART_NEOPIXEL
 	void configure(UART_Neopixel * neopixel);
// #endif

//#ifdef UART_DIGITAL_H
 	void configure(UART_Digital * digital);
//#endif
};

#endif /* UART-MESSAGEHANDLER_H */