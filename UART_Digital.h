/*
 * UART_Digital.h, header for UART_Digital
 *
 * UART_Digital is a library for controlling the digital I/O capable pins on an
 *  Arduino via the uart interface.  It can set pinmode, write high or low, and
 *  read the data from the pins dynamically.
 */

#ifndef UART_DIGITAL_H
#define UART_DIGITAL_H

#include <Arduino.h>

#define UART_D_SCMD_GET			0x00
#define UART_D_SCMD_SET			0x01
#define UART_D_SCMD_SAP			0x70
#define UART_D_SCMD_GAP			0x71
#define UART_D_SCMD_CPIN		0x7f
#define UART_D_SCMD_MANAGE		0xfd /* We want 0xfd to be the manage command on all classes */
#define UART_D_SCMD_ADD			0xfe
#define UART_D_SCMD_DEL			0xff

/* These sizes are in bytes */
#define UART_D_MSGS_GET			2
#define UART_D_MSGS_SET			4
#define UART_D_MSGS_ADD			4
#define UART_D_MSGS_DEL			4 //2 ints.
#define UART_D_MSGS_CPIN		4
#define UART_D_MSGS_SAP			6
#define UART_D_MSGS_GAP			4
#define UART_D_MSGS_MANAGE		6 // Manage pin size

/* I don't think we need this at all. */

/* I should just make this a class so we can locally call things. */
struct DIO_t
{
//  	uint8_t id; /* Pin ID (if you wanna use that) */
  	int pin; /* Pin number */
  	uint8_t dir; /* Direction [pinmode] */
  	int state; /* Last known state (analogread/analogwrite/high/low) and only set for devices where dir is input */
 	uint8_t pClass; /* Pin class [analog(1), digital(0)] */
  	DIO_t * next;
};

union int_u {
	int data;
	uint8_t raw[2];
};

union uint16_u {
	uint16_t data;
	uint8_t raw[2];
};

class UART_Digital
{
 private:
 	DIO_t * _pins;
 	HardwareSerial * _uart;
 	
 public:
 	UART_Digital();

 	void sUART(HardwareSerial * uart);

 	DIO_t * getPin(int pin);

 	uint8_t add(int pin, uint8_t direction, uint8_t pClass, int state=0);
 	int8_t del(int pin);

 	uint8_t set(DIO_t * in); /* This will handle analog and digital */
 	int get(DIO_t * in); /* This will handle analog and digital */



	uint8_t reportPin(DIO_t * in, uint8_t type=0); /* This method will print the data on _uart */

 	uint8_t cPin(DIO_t * in);

 	uint8_t handleMsg(uint8_t * buf, uint16_t llen);

};

#endif /* UART_DIGITAL_H */