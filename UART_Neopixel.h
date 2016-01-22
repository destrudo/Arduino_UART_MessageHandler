#ifndef UART_NEOPIXEL_H
#define UART_NEOPIXEL_H

#include <Arduino.h>
#include "Adafruit_NeoPixel.h"
//#include "UART_MessageHandler.h"

#define UART_NEOPIXEL_MSG_BEGIN 0xAA /* stream sequence start message is to send command */
#define UART_NEOPIXEL_MSG_END 	0x55 /* End sequence */

/* If you define DEBUG, you will need to call Serial.begin(<baud>) in Setup.
 *  It will use the Serial instance for doing prints, and I have made no easy
 *  way to change it [sorry].
 */
//#define DEBUG

/* Sub command definitions */
#define UART_NP_SCMD_CTRL		0x00
#define UART_NP_SCMD_CTRLI		0x01 /* Immediate control */
#define UART_NP_SCMD_CLEAR		0x02
#define UART_NP_SCMD_GET		0x03
#define UART_NP_SCMD_GET_ALL	0x04 /* Not implemented */
#define UART_NP_SCMD_MANAGE		0xfd /* This is the get strands command */
#define UART_NP_SCMD_ADD		0xfe
#define UART_NP_SCMD_DEL		0xff

/* UART_NeoPixel header data extension */
#define UART_NP_XHEADER_SIZE	1

#define UART_NP_GETALL_FILL		"//-//" /* This is the separator used by getAll */

/* Each individual command is this length in bytes */
#define UART_NP_CTRL_MSG_SIZE	5
#define UART_NP_GET_MSG_SIZE	0
#define UART_NP_GET_A_MSG_SIZE	0
#define UART_NP_ADD_MSG_SIZE	3 /* id(1), pin(1), length(2) */
#define UART_NP_DEL_MSG_SIZE	2 /* id(1), id(1) */
#define UART_NP_CLEAR_MSG_SIZE	0 /* The clear command is so innocuous that we don't check it. */
#define UART_NP_MANAGE_MSG_SIZE 6

/* UART_NeoPixel extended header struct */
struct UART_NP_XHeader_s
{
	uint8_t id;
};

/* UART_NeoPixel extended header union */
union UART_NP_XHeader
{
	uint8_t raw[UART_NP_XHEADER_SIZE];
	UART_NP_XHeader_s data;
};

/* We don't wanna keep it static for reasons of being really cool, so... LL. */
class strand_t
{
 public:
	uint8_t id;
	uint8_t pin;
	uint16_t len;
	Adafruit_NeoPixel * neopixel;
	strand_t * next;

	strand_t(uint8_t id, uint8_t pin, uint16_t len);

	~strand_t();

	void get(HardwareSerial * uart);

	strand_t * Next() /* We actually should be using this method, but it can wait. */
	{
		return next;
	}
};

class strandSet
{
 private:
	strand_t * head;
	uint8_t len;
  
 public:
	strandSet(void);
	void add(uint8_t id, uint8_t pin, uint16_t len); /* add a new strand instance */
	void del(uint8_t id); /* Destroy strand based on ID */
	void del();
	uint8_t lSize();
	void getAll(HardwareSerial * uart);
	strand_t * getStrand(uint8_t id); /* Search for strand id */
	strand_t * getHead();
 	uint8_t manageStrands(HardwareSerial * uart);

};

class UART_Neopixel
{
 private:
 	uint8_t * _buf;/* temporary, will go back to *buf */
 	HardwareSerial * _uart;
 	strandSet strandSet_i;
 public:
 	UART_Neopixel();
 	UART_Neopixel(HardwareSerial &uart, uint32_t baud=115200);
 	UART_Neopixel(HardwareSerial * uart);

 	void sUART(HardwareSerial * uart);
 	
 	void begin(HardwareSerial &uart);
 	// uint8_t handleMsg(uint16_t llen);
 	uint8_t handleMsg(uint8_t * buf, uint16_t llen);

// 	uint8_t manageStrands(uint8_t * buf, uint16_t buflen); /* This is a blank in the first rev */
// 	uint8_t manageStrands();
 	// uint16_t readMsgD();
 	// void clear();

 	void strandLedSet(strand_t * lStrand, uint16_t & pixel, uint32_t & color, bool show=false);

 	// uint8_t * getBuf();
};

#endif /* UART_NEOPIXEL_H */