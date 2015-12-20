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
	_uart->setTimeout(100); //I don't know if this timeout is reasonable.
}

void UART_MessageHandler::begin(uint16_t baud)
{
	_uart->end(); /* This is probably worthless */
	_uart->begin(baud);
}

uint8_t UART_MessageHandler::handleMsg(uint16_t len)
{
	UART_Header header;
	uint8_t i, status;
	/* Determine if it's a valid packet type */
	for (i = 0; i < UART_MH_HEADER_SIZE; i++)
	{
		header.raw[i] = _buf[i]; /* This is a little problem thing */
	}

/* Start here, put this in checkHeader */
	/* Check the checksum */
	i = lrcsum(header.raw, UART_MH_HEADER_SIZE - 2); /* Since we aren't checksumming the last key it's -2 */

	if (i != header.data.chksum)
	{
#ifdef DEBUG
		Serial.println(F("Non-matching lrcsum in handleMsg"));
#endif
		return 2;
	}

	if ( (header.data.key_start != UART_MH_HEADER_KEY_START) || (header.data.key_end != UART_MH_HEADER_KEY_END))
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
	if (status) {
		_uart->println("NAK");
	}
	else {
		_uart->println("ACK");
	}

	return 0;
}

uint16_t UART_MessageHandler::readMsg()
{
	uint16_t msgLen = 0, lmsgLen = 0;
	uint8_t fragments = 0, fragmentC = 0, val;
	unsigned long millisC = 0;
	bool umh_flag = true;

	//Read first 11 bytes and perform quick comparison to make sure that it's a UARTMH packet
	_buf = new uint8_t[12]; //Do a define for this initial buffer size.
	memset(_buf, 0, sizeof(uint8_t) * 12);

	//This should return valid message lengths
	msgLen = (uint16_t)_uart->readBytes((uint8_t *)_buf, 12);

	if(msgLen != 12) { /* If we didn't get a full length value, fuck it. */
		return msgLen; 
	}

	/* If we have a key mismatch */
	if( (_buf[UART_MH_HEADER_KEY_START_IDX] != UART_MH_HEADER_KEY_START) || (_buf[UART_MH_HEADER_KEY_END_IDX] != UART_MH_HEADER_KEY_END) )
	{
#ifdef DEBUG
		Serial.print(F("Not a uart_mh header."));
#endif
		umh_flag = false;
	}

	if (umh_flag) {
		fragments = _buf[UART_MH_FRAG_IDX];
		fragmentC = fragments;
#ifdef DEBUG
		Serial.print(F("Uart_mh header utilized.  Fragment count:"));
		Serial.println((unsigned int)fragmentC);
#endif
	}

	millisC = millis() + 1000;
	while(!_uart->available()) {
		delay(1);
		if (millis() > millisC) {
			Serial.println("Returning timed out readmessage 12.");
			return msgLen;
		}
	}

	do {
		delay(10);
#ifdef DEBUG
		Serial.print(F("Fragments currently: "));
		Serial.println(fragments);
#endif
		lmsgLen = msgLen;
		while(_uart->available() > 0)
		{
			val = _uart->read();
			_buf = (uint8_t *) realloc(_buf, (msgLen + 1) * sizeof(uint8_t));
			_buf[msgLen] = 0;
			_buf[msgLen] = (uint8_t)val;
#ifdef DEBUG
			Serial.print(F("uart in: 0x"));
			Serial.print(_buf[msgLen], HEX);
			Serial.print(F(", len: "));
			Serial.println(msgLen);
#endif
			msgLen++;
			/* boom.  We're done.  64 bytes (max). */
		}

		if(umh_flag && (fragments > 0) )
		{
#ifdef DEBUG
				Serial.println(F("Fragment set and fragmentC."));
#endif
			if ( ( (msgLen) % (ARDUINO_SERIAL_RX_BUF_LEN-1) ) != 0 ) {

#ifdef DEBUG
				Serial.print(F("Message length:"));
				Serial.println(msgLen);
#endif

				if(fragments > 1) {
#ifdef DEBUG
					Serial.println(F("Fragments still in buffer, but got an uneven packet."));
					Serial.print(F("msglen: "));
					Serial.println(msgLen);
#endif
					_uart->flush(); //Flush first!!!
					delay(10);
					_uart->print(F(UART_MH_FRAG_BAD));
					msgLen = lmsgLen; //Reset the message counter
					
					millisC = millis() + 3000; 
					while(_uart->available() < 63) {
						delay(1);
#ifdef DEBUG
						Serial.println(F("00 waiting for avail."));
#endif		
						if (millis() > millisC) {
#ifdef DEBUG
							Serial.println(F("00 ending because of too much time"));
#endif
							goto uarttimeout;
						}

					}

				} else {
#ifdef DEBUG
					Serial.println(F("Fragment last packet acquired."));
#endif
					_uart->flush();
					delay(1); //This was 10
					_uart->print(F(UART_MH_FRAG_OK));
					break;
				}
			}
			else
			{
#ifdef DEBUG
				Serial.println(F("Fragment else."));
#endif
				_uart->flush();
				delay(1); //This was 10.
				_uart->print(F(UART_MH_FRAG_OK));
				millisC = millis() + 2000;

				if (fragments == 1) { /* If we are on the last fragment */
					Serial.println("Last fragment acquired.");
					break;
				}

				while(!_uart->available()) {
					delay(1);
#ifdef DEBUG
					Serial.println(F("02 waiting for avail."));
#endif						

					if (millis() > millisC) {
#ifdef DEBUG
						Serial.println(F("02 ending because of too much time"));
#endif
						goto uarttimeout;
					}
				}
				fragments--;
			}
		}
	} while(fragments > 0);

	return msgLen;

uarttimeout:
	clear();
	_uart->print(F(UART_MH_FRAG_BAD));
#ifdef DEBUG
	Serial.println(F("uarttimeout reached."));
#endif
	return 0;

}

uint16_t UART_MessageHandler::run(uint8_t & status)
{
	uint16_t i = 0;
	uint16_t msgLen = readMsg();
	uint8_t retc = 0;

#ifdef DEBUG
	Serial.print(F("Run called handleMsg(), length: "));
	Serial.println(msgLen);

	Serial.println(F("buffer content in run:"));
	for (i = 0; i < msgLen; i++) {
		Serial.print("buf (");
		Serial.print(i);
		Serial.print(") = 0x");
		Serial.println(_buf[i], HEX);
	}
#endif
	status = handleMsg(msgLen);

#ifdef DEBUG
	Serial.print(F("Run handleMsg() returned: "));
	Serial.println((unsigned long int) status);
#endif

	if (status != 0)
	{
#ifdef DEBUG
		Serial.print(F("Nonzero status reported by messagehandler run: "));
		Serial.println((long unsigned int)status, HEX);
#endif
		return msgLen;
	}

	/* If you wanted to do something nonstandard with the uart_mh message, remove this clear and return msgLen */
	clear();
	return 0;
}

void UART_MessageHandler::clear()
{
	if (_buf != NULL)
	{
#ifdef DEBUG
		Serial.println(F("Emptied buffer."));
#endif
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
	_neopixel->sUART(_uart);
}
// #endif

//#ifdef UART_DIGITAL_H
void UART_MessageHandler::configure(UART_Digital * digital)
{
	_digital = digital;
}
//#endif