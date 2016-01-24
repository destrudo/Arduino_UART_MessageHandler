#include <Arduino.h>
#include "UART_Digital.h"

#ifndef UART_MESSAGEHANDLER_H
 #include "UART_MessageHandler.h"
#endif

/* Constructor
 * 
 */
UART_Digital::UART_Digital()
{
	_pins = NULL;
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

/* getPin
 *
 * @pin, int, pin to get data from.
 * @ret, DIO_t* of pin if found, or null.
 *
 * Searches through the pins linked list and returns a pointer to it if found.
 */
DIO_t * UART_Digital::getPin(int pin)
{
	DIO_t * node = _pins;

	if(node == NULL) {
		return NULL;
	}

	if(node->pin == pin)
	{
		return node;
	}

	while (node->next != NULL)
	{
		if (node->pin == pin)
		{
			return node;
		}
		node = node->next;
	}

	if (node->pin == pin)
	{
		return node;
	}

	return NULL;
}

/* add
 * @pin, int, pin number
 * @direction, uint8_t, direction to use (INPUT/OUTPUT)
 * @pClass, uint8_t, type to use (DIGITAL/ANALOG)
 * @state, if nonzero, applies state to the pin via set()
 * @ret, if failure it returns nonzero.
 *
 * Add a pin to the _pins ll.
 */
uint8_t UART_Digital::add(int pin, uint8_t direction, uint8_t pClass, int state=0)
{
	DIO_t * node = _pins;
	DIO_t * lNode = NULL;

	if (getPin(pin))
	{
		return 1;
	}

	lNode = new DIO_t;
	lNode->pin = pin;
	lNode->dir = direction;
	lNode->pClass = pClass;
	lNode->state = state;
	lNode->next = NULL;

	/* Perform initial pinMode setting */
	pinMode(pin, direction);

	/* If a state was specified when adding this pin... */
	if (state) {
		set(lNode);
	}

	if (node == NULL)
	{
		_pins = lNode;
		return 0;
	}


	/* This puts the node at the very end */
	while (node->next != NULL)
	{
		node = node->next;
	}

	node->next = lNode;

	return 0;
}

/* del()
 *
 * @pin, int.
 * @ret, success/failure(Nonzero)
 *
 * Deletes a pin if it exists.
 */
int8_t UART_Digital::del(int pin)
{
	DIO_t * node = _pins;
	DIO_t * prev = NULL;

	while ( (node != NULL) && (node->pin != pin) )
	{
		prev = node;
		node = node->next;
	}

	if ( node == NULL )
	{
		return -1;
	}

	if ( prev == NULL )
	{
		_pins = node->next;
	}
	else
	{
		prev->next = node->next;
	}

	delete(node);
	node = NULL;

	return 0;
}

/* set()
 *
 * @in, DIO_t pointer to value
 * @ret, Pass/fail(Nonzero)
 *
 * This sets the DIO_t* values via Write commands.
 */
uint8_t UART_Digital::set(DIO_t * in)
{
	if (in == NULL) {
		return 1;
	}

	/* For this, we actually do wanna check the direction */
	if ( (in->pClass == 0) && (in->dir == OUTPUT) )
	{
		digitalWrite(in->pin, in->state);
		return 0;
	}
	
	if (in->dir == OUTPUT)
	{
		analogWrite(in->pin, in->state);
		return 0;
	}

	return 1;
}

/* get()
 *
 * @in, DIO_t pointer to value
 * @ret, value read, negative numbers are failures.
 *
 * This performs a read based on DIO_t* values and then returns it.
 */
int UART_Digital::get(DIO_t * in)
{
	if (in == NULL) {
		return -1;
	}

	/* We could prevent reads based on pinMode (Dir), but it seems pointless because of the different possible values. */
	if (in->pClass == 0)
	{
		in->state = digitalRead(in->pin);
	}
	/* We might want an additional pClass/direction validation to determine if it's actually an analogRead()-able pin */
	else
	{
		/* Perform the analog stuff */
		in->state = analogRead(in->pin);
	}

	return in->state;
}

/* cPin()
 *
 * @in, DIO_t pointer to value
 * @ret, pass/fail
 *
 * This uses a pre-created DIO_t to reset the member value and then change pinMode
 */
uint8_t UART_Digital::cPin(DIO_t * in)
{
	if (in == NULL)
		return 1;

	pinMode(in->pin, in->dir);

	/* If state was reported as set, and it's in an output mode... */
	if (in->dir == OUTPUT)
	{
		if (in->pClass == 1)
			analogWrite(in->pin, in->state);
		else
			digitalWrite(in->pin, in->state); //Hopefully this autocorrects if it's not given HIGH or LOW

	}

	return 0;
}

/* lSize()
 * 
 * @ret, size of _pins ll
 *
 * returns size of _pins linked list.
 */
uint8_t UART_Digital::lSize()
{
	uint8_t counter = 0;
	DIO_t * node = _pins;
	if (node != NULL)
		counter++;
	else
		return 0;

	while(node->next != 0)
	{
		node = node->next;
		counter++;
	}

	return counter;
}

/* manage()
 *
 * Sends management message over _uart.  Reports all pin values.
 */
uint8_t UART_Digital::manage()
{
	DIO_t * node = _pins;
	uint8_t ib = lSize();
	uint8_t ia[2];
	int_u intuI;

	if (ib == 0)
	{
		return 1;
	}

	_uart->write(ib);

	while (node != NULL)
	{
		reportPin(node, 1);
		node = node->next;
	}
}

/* reportPin()
 *
 * @in, DIO_t pointer
 * @type, method in which to report
 * @ret, pass/fail(nonzero)
 *
 * This method calls _uart print methods.  If type is nonzero, it prints out all DIO_t data.
 */
uint8_t UART_Digital::reportPin(DIO_t * in, uint8_t type)
{
	/* We might not need these variables, but I'm gonna keep em' here for the initial stuff */
	int_u data;

	if ( (_uart == NULL) || (in == NULL) )
		return 1;

	/* if type is non-zero, then we want to perform a complete DIO_t type dump */
	if (type)
	{
		data.data = in->pin;
		_uart->write(data.raw, 2); // pin
		_uart->write(in->dir); // dir
		data.data = in->state;
		_uart->write(data.raw, 2); //state
		_uart->write(in->pClass); //pclass
	}
	/* Otherwise, we just want simple state data. */
	else
	{
		data.data = in->state;
		_uart->write(data.raw, 2); //Needed to be 2 bytesssss
	}

	return 0;
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
	uint8_t status = 0;
	int pin, ret, mode;
	uint16_u uint16Ret;
	int_u intRet, intRet2;
	uint8_t val;
	uint16_t oBufL, i;

	DIO_t * tPin = NULL;

	for (i = 0; i < UART_MH_HEADER_SIZE; i++)
	{
		header.raw[i] = buf[i];
	}

	switch(header.data.scmd)
	{
		case UART_D_SCMD_GET:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_GET) != 0) || ( (llen - UART_MH_HEADER_SIZE)/UART_D_MSGS_GET != header.data.in) || (header.data.out != header.data.in) )
				return 1;

			for (i; i < llen; i+=UART_D_MSGS_GET)
			{
				pin = (int)buf[i] << 8 | (int)buf[i+1];
				tPin = getPin(pin);

				if (tPin == NULL)
					return 3;

				intRet.data = get(tPin);

				status = reportPin(tPin);
			}

		 break;

		case UART_D_SCMD_SET:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_SET) != 0) || (header.data.in != 0) )
				return 1;

			for (i; i < llen; i+=UART_D_MSGS_SET)
			{
				pin = (int)buf[i] << 8 | (int)buf[i+1];

				tPin = getPin(pin);

				if (tPin == NULL)
					return 3;

				tPin->state = (int)buf[i+2] << 8 | (int)buf[i+3];

				status = set(tPin);
			}
		 break;

		case UART_D_SCMD_ADD:
			// Serial.println("SCMD ADD");

			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_ADD) != 0) || (header.data.in != 0) ) {
				// Serial.println("BAD HEADER IN ADD");
				return 1;
			}

			for (i; i < llen; i+=UART_D_MSGS_ADD)
			{
				intRet.raw[0] = buf[i];
				intRet.raw[1] = buf[i+1];

				tPin = getPin(intRet.data);

				if (tPin != NULL) {
					// Serial.println("ADD TPIN NULL");
					return 4;
				}

				status = add(intRet.data, buf[i+2], buf[i+3]);
			}

		 break;

		case UART_D_SCMD_DEL:
			if ( llen != (UART_MH_HEADER_SIZE + UART_D_MSGS_DEL) )
				return 1;

			// We have i set from before.
			intRet.raw[0] = buf[i];
			intRet.raw[1] = buf[i+1];

			intRet2.raw[0] = buf[i+2];
			intRet2.raw[1] = buf[i+3];

			//I guess we should /technically/ do 4 just to keep consistent... but at this point it's pointless.

			if (intRet.data != intRet2.data)
				return 2;

			status = del(intRet.data);

		 break;

		/* Change a pin */
		case UART_D_SCMD_CPIN:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_CPIN) != 0) || (header.data.in != 0) ) {
				return 1;
			}

			for (i; i < llen; i+=UART_D_MSGS_CPIN)
			{
				intRet.raw[0] = buf[i];
				intRet.raw[1] = buf[i+1];

				tPin = getPin(intRet.data);

				if (tPin == NULL) {
					return 3; /* we can't change a pin that hasn't already been created */
				}

				tPin->dir = buf[i+2];
				tPin->pClass = buf[i+3];
				tPin->state = 0; /* We default the state to zero here */

				status = cPin(tPin);
			}


		 break;

		case UART_D_SCMD_GAP:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_GAP) != 0) || (header.data.in != 0) )
				return 1;

			for (i; i < llen; i+=UART_D_MSGS_GAP)
			{
				intRet.raw[0] = buf[i];
				intRet.raw[1] = buf[i+1];
				
				if (add(intRet.data, buf[i+2], buf[i+3], 0))
					return 2;

				tPin = getPin(intRet.data);
				get(tPin);
				status = reportPin(tPin);
			}


		 break;

		case UART_D_SCMD_SAP:
			if ( (((llen - UART_MH_HEADER_SIZE) % UART_D_MSGS_SAP) != 0) || (header.data.in != 0) )
				return 1;

			for (i; i < llen; i+=UART_D_MSGS_SAP)
			{
				intRet.raw[0] = buf[i];
				intRet.raw[1] = buf[i+1];
					//2
					//3
				intRet2.raw[0] = buf[i+4];
				intRet2.raw[1] = buf[i+5];

				/* Since we're setting state, the add() call will handle setting it */
				status = add(intRet.data, buf[i+2], buf[i+3], intRet2.data);
			}

		 break;

		case UART_D_SCMD_MANAGE:
			if ( (llen - UART_MH_HEADER_SIZE) != UART_D_MSGS_MANAGE)
				return 1;

			for (i; i < llen; i++)
			{
				if (buf[i] != UART_D_SCMD_MANAGE)
					return 2;
			}

			if (manage())
			{
				return 254;
			}
			
		 break;

		default:
			return 1;
	}

	return status;
}
