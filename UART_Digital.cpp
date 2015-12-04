#include <Arduino.h>
#include "UART_Digital.h"

#ifndef UART_MESSAGEHANDLER_H
 #include "UART_MessageHandler.h"
#endif

UART_Digital::UART_Digital()
{

}

/* sUART
 *
 * @uart, HardwareSerial *
 *
 * Saves uart HardwareSerial instance pointer to class local
 */
void UART_Digital::sUART(HardwareSerial * uart)
{
	_uart = uart;
}

//uint8_t UART_Digital::init(int pin, int direction, int state, bool pClass)
uint8_t UART_Digital::init(int pin, int direction)
{
	DIO_t * pinD = getAddPin(pin);
	pinD->dir = direction;
	pinMode(pinD->pin, pinD->dir);
}

/* This method attempts a getPin, if it fails, it creates a new pin and then
	returns a pointer to that pin.  */
DIO_t * UART_Digital::getAddPin(int pin)
{
	DIO_t * pinI = getPin(pin);
	if (pinI == NULL)
	{
		add(pin, 0, 0); /* Default the pin to zeroes. */
		pinI = getPin(pin);
		if (pinI == NULL)
		{
#ifdef DEBUG
			Serial.println(F("Unexpected failure in getAddPin."));
#endif
		}
	}

	return pinI;
}

DIO_t * UART_Digital::getPin(int pin)
{
	DIO_t * node = _pins;
#ifdef DEBUG
	Serial.print(F("getPin pin search: "));
	Serial.println(pin);
#endif

	if(node == NULL) {
#ifdef DEBUG
		Serial.println(F("getPin, head null."));
#endif
		return NULL;
	}

	if(node->pin == pin)
	{
#ifdef DEBUG
		Serial.println(F("getPin returning head for pin."));
#endif
		return node;
	}

	while (node->next != NULL)
	{
#ifdef DEBUG
		Serial.println(F("getPin while iter."));
		Serial.print(F("cur pin: "));
		Serial.println(node->pin);
#endif
		if (node->pin == pin)
		{
#ifdef DEBUG
			Serial.println(F("Pin match!"));
#endif
			return node;
		}
		node = node->next;
	}

	if (node->pin == pin)
	{
#ifdef DEBUG
		Serial.println(F("getPin match post while."));
#endif
		return node;
	}

	return NULL;
}

void UART_Digital::add(int pin, int dir, int state)
{
	DIO_t * node = _pins;
	DIO_t * lNode = NULL;

	if (getPin(pin))
	{
#ifdef DEBUG
		Serial.println(F("digital pin already defined."));
#endif
		return;
	}

	lNode = new DIO_t;
	lNode->pin = pin;
	lNode->dir = dir;
	lNode->state = state;
	lNode->next = NULL;

	if (node == NULL)
	{
#ifdef DEBUG
		Serial.println(F("digital add head null."));
#endif
		_pins = lNode;
		return;
	}

	while (node->next != NULL)
	{
#ifdef DEBUG
		Serial.println(F("digital add while"));
#endif
		node = node->next;
	}

	node->next = lNode;
}

void UART_Digital::set(int pin, int mode)
{
	digitalWrite(pin, mode);
}

// void UART_Digital::set(uint8_t id, int mode)
// {

// }

int UART_Digital::get(int pin)
{
	return digitalRead(pin);
}

// int UART_Digital::get(uint8_t id)
// {

// }

/* aGet
 *
 * @pin, int
 * @ret, uint16_t
 *
 * runs analogRead() against a pin and then returns the value.
 */
uint16_t UART_Digital::aGet(int pin)
{
	return analogRead(pin);
}

/* aSet
 *
 * @pin, int
 * @value, uint8_t
 *
 * runs analogWrite() against a pin with value
 */
void UART_Digital::aSet(int pin, uint8_t value)
{
	analogWrite(pin, value);
}

/* handleMsg
 *
 * @buf, uint8_t*
 * @llen, uint16_t, length of buf
 * @ret, uint8_t, return code
 *
 * handleMsg() takes the command input string [uint8_t *] and translates
 *  the subcommands.
 */
uint8_t UART_Digital::handleMsg(uint8_t * buf, uint16_t llen)
{
	UART_Header header;

	uint8_t * oBuf; /* This is the output buffer */

	int pin, ret, mode;
	uint16_u uint16Ret;
	int_u intRet;
	uint8_t val;
	uint16_t oBufL, i;

	for (i = 0; i < UART_MH_HEADER_SIZE; i++)
	{
		header.raw[i] = buf[i];
	}

	switch(header.data.scmd)
	{
		case UART_D_SCMD_GET_D:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_GET_D) != 0) || ( (llen - UART_MH_HEADER_SIZE)/UART_D_MSGS_GET_D != header.data.in) || (header.data.out != header.data.in) )
				return 1;

			/* OLD Initialize the output buffer completely. */
			/*
			oBuf = new uint8_t[header.in];
			*/

			for (i; i < llen; i+=UART_D_MSGS_GET_D)
			{
				pin = (int)buf[i] << 8 | (int)buf[i+1];
				//ret = get(pin);
				intRet.data = get(pin);

				/* Old pre-prep and send */
				/*
				oBuf[i] = intRet.raw[0];
				oBuf[i+1] = intRet.raw[1];
				*/

				/* Immediately write the data to the serial interface */
				//_uart->write(intRet.raw[0]);
				//_uart->write(intRet.raw[1]);
				_uart->write(intRet.raw, 2);
			}

			/* OLD Send data via serial out */

		 break;

		case UART_D_SCMD_SET_D:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_SET_D) != 0) || (header.data.in != 0) )
				return 1;

			for (i; i < llen; i+=UART_D_MSGS_SET_D)
			{
				pin = (int)buf[i] << 8 | (int)buf[i+1];
				mode = (int)buf[i+2] << 8 | (int)buf[i+3];

				set(pin, mode);
			}
		 break;

		case UART_D_SCMD_GET_A:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_GET_A) != 0) || ( (llen - UART_MH_HEADER_SIZE)/UART_D_MSGS_GET_A != header.data.in) || (header.data.out != header.data.in) )
				return 1;

			for (i; i < llen; i+=UART_D_MSGS_GET_A)
			{
				pin = (int)buf[i] << 8 | (int)buf[i+1];

				uint16Ret.data = aGet(pin);

				_uart->write(uint16Ret.raw, 2);
			}
		 break;

		case UART_D_SCMD_SET_A:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_SET_A) != 0) || (header.data.in != 0) )
				return 1;

			for (i; i < llen; i+=UART_D_MSGS_SET_A)
			{
				pin = (int)buf[i] << 8 | (int)buf[i+1];
				aSet(pin, buf[i+2]);
			}
		 break;

		case UART_D_SCMD_PINM:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_PINM) != 0) || (header.data.in != 0) )
				return 1;

			for (i; i < llen; i+=UART_D_MSGS_PINM)
			{
				intRet.raw[1] = buf[i];
				intRet.raw[0] = buf[i+1];
				pin = intRet.data;
				intRet.raw[1] = buf[i+2];
				intRet.raw[0] = buf[i+3];
				pinMode(pin,intRet.data);
			}
		 break;

		default:
			delay(1);
	}
}
