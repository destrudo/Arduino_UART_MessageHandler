/*
 * UART-MessageHandler.cpp, implementations for UART-MessageHandler
 *
 * UART-MessageHandler is a library for a protocol on top of UART for
 *  controlling various arduino-related instances.  Each message is (poorly)
 *  checksummed and contains message length data as well as expected return
 *  data lengths.
 */
#include <Arduino.h>
#include "UART_MessageHandler.h"

uint8_t lrcsum(uint8_t * data, uint8_t datasz)
{
	uint8_t chksum = 0;
	while (datasz > 0)
	{
		chksum ^= *data++;
		datasz--;
	}

	return chksum;
}

UART_MessageHandler::UART_MessageHandler()
{
	_neopixel = NULL; /* These can be set in the method def because constructor. */
	_digital = NULL;
}

UART_MessageHandler::UART_MessageHandler(HardwareSerial * uart, uint16_t baud)
{
	_neopixel = NULL;
	_digital = NULL;

	setUART(uart);
	begin(baud);
}

void UART_MessageHandler::setUART(HardwareSerial * uart)
{
	_uart = uart;
}

void UART_MessageHandler::begin(uint16_t baud)
{
	_uart->end(); /* This is probably worthless */
	_uart->begin(baud);
}

/*
uint8_t UART_MessageHandler::checkHeader()
{

}
*/

uint8_t UART_MessageHandler::handleMsg(uint16_t len)
{
	UART_Header header;
	uint8_t i, status;
	/* Determine if it's a valid packet type */
	for (i = 0; i < UART_MH_HEADER_SIZE; i++)
	{
		header.raw[i] = _buf[i];
	}

/*
	if(checkHeader(&header.raw))
		return 1;
*/

/* Start here, put this in checkHeader */
	/* Check the checksum */
	i = lrcsum(header.raw, UART_MH_HEADER_SIZE - 1);

	if (i != header.data.chksum)
		return 2;

	if (header.data.key != UART_MH_HEADER_KEY)
		return 3;

/* To here... */
#ifdef DEBUG
	Serial.print(F("Header cmd: "));
	Serial.println(header.data.cmd, HEX);
#endif

	switch (header.data.cmd) {

		case CMD_UART_MESSAGEHANDLER:
			/* do stuff for configuring UART_MessageHandler */
		 break;

		case CMD_UART_DIGITAL:
			if (_digital == NULL) {
#ifdef DEBUG
				Serial.println(F("Unable to handle, Digital not configured"));
#endif
				status = 0xfe;
				break;
			}

//#ifdef UART_DIGITAL_H
		/* Do stuff for uart digital */
			status = _digital->handleMsg(_buf, len);
//#endif
		 break;

		case CMD_UART_NEOPIXEL:
			if (_neopixel == NULL) {
#ifdef DEBUG
				Serial.println(F("Unable to handle, Neopixel not configured"));
#endif
				status = 0xff;
				break;
			}
// #ifdef USE_UART_NEOPIXEL_H
		/* do stuff for uart neopixel */
			status = _neopixel->handleMsg(_buf, len);
// #endif
		 break;

		/* If you want to add additional modules, this is where. */

		default:
			Serial.println("Meow.");
	}

	/* We should have a status variable that gets passed through so that we can return a NAK on failure */
	//_uart->println("ACK");

	/* Replacement logic for the above */
	if (status)
		_uart->println("NAK");
	else
		_uart->println("ACK");
}

uint16_t UART_MessageHandler::readMsg()
{
	uint16_t msgLen = 0;
	uint8_t val;

	_buf = new uint8_t[1];

	while (_uart->available() > 0)
	{
		val = _uart->read();
		_buf = (uint8_t *) realloc(_buf, (msgLen + 1) * sizeof(uint8_t));
		_buf[msgLen] = 0;
		_buf[msgLen] = (uint8_t)val;

#ifdef DEBUG
		Serial.print(F("readMsg while got: "));
		Serial.print(_buf[msgLen]);
		Serial.print(F(", 0x"));
		Serial.println(_buf[msgLen], HEX);
#endif
		msgLen++;

		if (msgLen >= UART_MH_MAX_MSG_SIZE)
		{
#ifdef DEBUG
			Serial.print(F("readMsg() breaking at: "));
			Serial.println(msgLen);
#endif
			break;
		}
	}

#ifdef DEBUG
	Serial.print(F("readMsg() returning: "));
	Serial.println(msgLen);
#endif

	return msgLen;
}

uint16_t UART_MessageHandler::run(uint8_t * status)
{
	uint16_t msgLen = readMsg();
	*status = handleMsg(msgLen);

	if (&status != 0)
		return msgLen;

	return 0;
}

void UART_MessageHandler::clear()
{
	if (_buf != NULL)
	{
		delete _buf;
		_buf = NULL;
	}
}

uint8_t * UART_MessageHandler::getBuf()
{
	return _buf;
}

// #ifdef USE_UART_NEOPIXEL
void UART_MessageHandler::configure(UART_Neopixel * neopixel)
{
	_neopixel = neopixel;
}
// #endif

//#ifdef UART_DIGITAL_H
void UART_MessageHandler::configure(UART_Digital * digital)
{
	_digital = digital;
}
//#endif