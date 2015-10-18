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

#define UART_D_SCMD_GET_D		0x00
#define UART_D_SCMD_SET_D		0x01
#define UART_D_SCMD_GET_A		0x02
#define UART_D_SCMD_SET_A		0x03
#define UART_D_SCMD_PINM		0xFF

/* These sizes are in bytes */
#define UART_D_MSGS_GET_D		2
#define UART_D_MSGS_SET_D		4
#define UART_D_MSGS_GET_A		2
#define UART_D_MSGS_SET_A		3
#define UART_D_MSGS_PINM		4




/* I don't think we need this at all. */

// struct DIO_t
// {
//  	uint8_t id; /* Pin ID (if you wanna use that) */
//  	int pin; /* Pin number */
//  	int dir; /* Direction [pinmode] */
//  	int state; /* Last known state */
// 	int pClass; /* Pin class [analog(1), digital(0)] */
//  	DIO_t * next;
// };

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
 	//DIO_t * _pins;
 	HardwareSerial * _uart;
 	
 public:
 	UART_Digital();

 	void sUART(HardwareSerial * uart);

	//uint8_t init(int pin, int direction, int state, bool pClass); /* Initialize a pin (Adds it to the end of the ll) */
	uint8_t init(int pin, int direction);

 	void set(int pin, int mode); /* Set a pin [by pin number] */
 	//void set(uint8_t id, int mode); /* Set a pin [by id] */

 	int get(int pin); /* Get a pin's current value */
 	//int get(uint8_t id); /* Get a pin's current value [by id] */

 	uint16_t aGet(int pin); /* Analog get */

 	void aSet(int pin, uint8_t value);

 	uint8_t handleMsg(uint8_t * lbuf, uint16_t llen);

};

#endif /* UART_DIGITAL_H */