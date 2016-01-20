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

#define UART_MH_HEADER_SIZE 12
#define UART_MH_HEADER_KEY_START 0xAA
#define UART_MH_HEADER_KEY_END 0xFB

#define UART_MH_BODY_END 0xDEAD

#define UART_MH_FRAG_OK "CT\r\n"
#define UART_MH_FRAG_BAD "FF\r\n"
#define ARDUINO_SERIAL_RX_BUF_LEN 64

#define UART_MH_HEADER_KEY_START_IDX 0
#define UART_MH_HEADER_KEY_END_IDX 11
#define UART_MH_FRAG_IDX 1

#define UART_MH_MAX_MSG_SIZE 512

#define CMD_UART_MESSAGEHANDLER 0x00
#define CMD_UART_DIGITAL 0x01
#define CMD_UART_NEOPIXEL 0x02

#define UART_MH_SCMD_MANAGE 0xFF

#define READMSG_POSTDATA_INTERVAL 1000UL
#define FRAGMENT_INTERVAL 2000UL

/* If you're using the eeprom, make sure you change this */
#define UART_MH_EEPROM_OFFSET 0x00

#define IDSIZE 4
#define TYPE 0x1 /* If you want some custom identifier for support, change this in your code fork */


//#define DEBUG

struct eeprom_t {
  uint8_t type: 4; /* This is a non-unique portion */
  uint32_t id: 28;
};

union eeprom_u {
  struct eeprom_t data;
  uint32_t number;
  uint8_t raw[IDSIZE];
};

/* lrc checksum */
uint8_t lrcsum(uint8_t * data, uint8_t datasz);

uint32_t _generateKey();
uint32_t _getKey();
void _setKey(uint32_t keyIn);

struct UART_Header_s
{
	uint8_t key_start;
	uint8_t msg_frag;

//	uint8_t key;
	uint16_t cmd;
	uint8_t scmd;
	uint8_t version;
	uint16_t out;
	uint16_t in;
	uint8_t chksum;

	uint8_t key_end; /* This will NOT be part of the checksum */
};

union UART_Header
{
	uint8_t raw[UART_MH_HEADER_SIZE];
	UART_Header_s data;
};

union int_u
{
	uint8_t raw[2];
	int data;
};

union uint32_u
{
	uint32_t data;
	uint8_t raw[4];
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
 	eeprom_u identity;

 public:
 	UART_MessageHandler();
 	UART_MessageHandler(HardwareSerial * uart, uint16_t baud);

 	void setUART(HardwareSerial * uart);
 	void begin(uint16_t baud);

 	/* uint8_t checkHeader(UART_Header_s * header); */

 	uint8_t handleMsg(uint16_t len);
 	uint16_t readMsg();
 	uint8_t * getBuf();

 	void configure();

 	uint8_t manage();

 	uint16_t run(uint8_t & status);

 	uint32_t ident();
 	void setIdent();

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