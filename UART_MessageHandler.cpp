/*
 * UART-MessageHandler.cpp, implementations for UART-MessageHandler
 *
 * UART-MessageHandler is a library for a protocol on top of UART for
 *  controlling various arduino-related instances.  Each message is (poorly)
 *  checksummed and contains message length data as well as expected return
 *  data lengths.
 */
#include <Arduino.h>
#include <EEPROM.h>
#include "UART_MessageHandler.h"
#include "UART-BaseC.h"

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

/* We need to lock this stuff out for non-avr stuff */
uint32_t _generateKey()
{
	eeprom_u data;

	randomSeed((analogRead(0) + analogRead(1) + analogRead(2)) * analogRead(3) );

    data.number = ((random((unsigned long)pow(2, 2 * 8)) - 1) << 16 | (random((unsigned long)pow(2, 2 * 8)) - 1));

    data.data.type = TYPE;

    return data.number;
}

uint32_t _getKey()
{
	eeprom_u data;
	for (int i = UART_MH_EEPROM_OFFSET + IDSIZE - 1; i >= UART_MH_EEPROM_OFFSET; i--)
	{
		data.raw[i - UART_MH_EEPROM_OFFSET] = EEPROM.read(i);
	}

	return data.number;
}

void _setKey(uint32_t key)
{
	eeprom_u data;

	data.number = key;

	
	for (int i = UART_MH_EEPROM_OFFSET; i < (UART_MH_EEPROM_OFFSET + IDSIZE); i++)
	{
		EEPROM.write(i, data.raw[i - UART_MH_EEPROM_OFFSET]);
	}
}

UART_MessageHandler::UART_MessageHandler()
{
	_neopixel = NULL; /* These can be set in the method def because constructor. */
	_digital = NULL;

	_buf = NULL;

}

UART_MessageHandler::UART_MessageHandler(BaseSerial_ * uart, uint16_t baud)
// UART_MessageHandler::UART_MessageHandler(HardwareSerial * uart, uint16_t baud)
{
	_neopixel = NULL;
	_digital = NULL;

	_buf = NULL;

	setUART(uart);
	begin(baud);
}


void UART_MessageHandler::setIdent() {
	eeprom_u data;
	data.number = _getKey();

	/* Checks to see if it's all zeroes (not set). */
	if (data.number == 0)
	{
		_setKey(_generateKey());
		data.number = _getKey();
	}

    identity = data;
}

uint32_t UART_MessageHandler::ident()
{
	return identity.number;
}

void UART_MessageHandler::setUART(BaseSerial_ * uart)
// void UART_MessageHandler::setUART(HardwareSerial * uart)
{
	_uart = uart;
	_uart->setTimeout(100); //I don't know if this timeout is reasonable.

	/* I'm doing this here since it'll get called no matter what */
	setIdent();
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

	/* Check the checksum */
	i = lrcsum(header.raw, UART_MH_HEADER_SIZE - 2); /* Since we aren't checksumming the last key it's -2 */

	if (i != header.data.chksum) {
		return 2;
	}

	if ( (header.data.key_start != UART_MH_HEADER_KEY_START) || (header.data.key_end != UART_MH_HEADER_KEY_END))
		return 3;

	switch (header.data.cmd) {

		case CMD_UART_MESSAGEHANDLER:
			/* We might want to introduce a switch here if it exceeds 3 options for cleanliness. */
			/* do stuff for configuring UART_MessageHandler */
			if (header.data.scmd == UART_MH_SCMD_MANAGE) {
				status = manage();
			}
		 break;

		case CMD_UART_DIGITAL:
			if (_digital == NULL) {
				status = 0xfe;
				break;
			}

			/* Do stuff for uart digital */
			status = _digital->handleMsg(_buf, len);

		 break;

		case CMD_UART_NEOPIXEL:
			if (_neopixel == NULL) {
				status = 0xff;
				break;
			}
			/* do stuff for uart neopixel */
			status = _neopixel->handleMsg(_buf, len);

		 break;

		/* If you want to add additional modules, this is where. */

		default:
			return 1;
	}

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
	unsigned long pMillis = 0;
	bool umh_flag = true;

	//Read first 11 bytes and perform quick comparison to make sure that it's a UARTMH packet
	_buf = new uint8_t[12]; //Do a define for this initial buffer size.

	memset(_buf, 0, sizeof(uint8_t) * 12);

	// delay(500);

	//This should return valid message lengths
	msgLen = (uint16_t)_uart->readBytes((uint8_t *)_buf, 12);

	if(msgLen != 12) { /* If we didn't get a full length value, fuck it. */
		Serial1.println("Message len is not 12... not our data.");
		Serial1.print("Message len: ");
		Serial1.println(msgLen);
		return msgLen; 
	}

	/* If we have a key mismatch */
	if( (_buf[UART_MH_HEADER_KEY_START_IDX] != UART_MH_HEADER_KEY_START) || (_buf[UART_MH_HEADER_KEY_END_IDX] != UART_MH_HEADER_KEY_END) )
	{
		umh_flag = false;
	}

	if (umh_flag) {
		fragments = _buf[UART_MH_FRAG_IDX];
		fragmentC = fragments;
	}

	pMillis = millis();
	while(!_uart->available()) {
		delay(1); //Tiny delay.

		if ((unsigned long)(millis() - pMillis) > READMSG_POSTDATA_INTERVAL)
			return msgLen;
	}

	do {
		delay(5);
		lmsgLen = msgLen;

		while(_uart->available() > 0)
		{
			val = _uart->read();
			_buf = (uint8_t *) realloc(_buf, (msgLen + 1) * sizeof(uint8_t));
			_buf[msgLen] = 0;
			_buf[msgLen] = (uint8_t)val;
			msgLen++;
		}

		if(umh_flag && (fragments > 0) )
		{
			if ( ( (msgLen) % (ARDUINO_SERIAL_RX_BUF_LEN-1) ) != 0 ) {
				if(fragments > 1) {
					_uart->flush();
					delay(10);
					_uart->print(F(UART_MH_FRAG_BAD));
					msgLen = lmsgLen; //Reset the message counter
					
					pMillis = millis();
					while(_uart->available() < 63) {
						delay(1);

						if ((unsigned long)(millis() - pMillis) > FRAGMENT_INTERVAL)
							goto uarttimeout;

					}

				} else {
					_uart->flush();
					delay(1); //This was 10
					_uart->print(F(UART_MH_FRAG_OK));
					break;
				}
			}
			else
			{
				_uart->flush();
				delay(1); //This was 10.
				_uart->print(F(UART_MH_FRAG_OK));

				if (fragments == 1) /* If we are on the last fragment */
					break;

				pMillis = millis();

				while(!_uart->available()) {
					delay(1);					

					if ((unsigned long)(millis() - pMillis) > FRAGMENT_INTERVAL)
						goto uarttimeout;

				}
				fragments--;
			}
		}
	} while(fragments > 0);

	return msgLen;

uarttimeout:
	clear();
	_uart->print(F(UART_MH_FRAG_BAD));
	return 0;

}

uint16_t UART_MessageHandler::run(uint8_t & status)
{
	uint16_t i = 0;
	uint16_t msgLen = readMsg();
	uint8_t retc = 0;

	status = handleMsg(msgLen);

	if (status != 0)
	{
		return msgLen;
	}

	/* If you wanted to do something nonstandard with the uart_mh message, remove this clear and return msgLen */
	clear();

	return 0;
}

uint16_t UART_MessageHandler::clear()
{
	if (_buf != NULL)
	{
		Serial1.println("Buffer is not null.");
		delete _buf;
		_buf = NULL;
	}
	return 0;
}

uint8_t * UART_MessageHandler::getBuf()
{
	return _buf;
}

uint8_t UART_MessageHandler::manage()
{
	/* If our ident is still 0, we have an inexplicable problem. */
	if (identity.number == 0)
		return 1;

	for (int i = 0; i < IDSIZE; i++)
	{
		_uart->write(identity.raw[i]);
	}

	return 0;
}

void UART_MessageHandler::configure(UART_Neopixel * neopixel)
{
	_neopixel = neopixel;
	_neopixel->sUART(_uart);
}

void UART_MessageHandler::configure(UART_Digital * digital)
{
	_digital = digital;
	_digital->sUART(_uart);
}