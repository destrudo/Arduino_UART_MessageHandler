#include <Arduino.h>
//#include "Adafruit_NeoPixel.h"
#include "UART_Neopixel.h"
#include "UART_MessageHandler.h"

/*********************/
/* strand_t  Methods */
/*********************/

/* Constructor
 *
 * @id, uint8_t, identifier to use
 * @pin, uint8_t, pin to use
 * @len, uint16_t, length of neopixel strip
 */
strand_t::strand_t(uint8_t id, uint8_t pin, uint16_t len)
{
#ifdef DEBUG
	Serial.print(F("Strand init, (id, pin, len) - "));
	Serial.print(id);
	Serial.print(F(","));
	Serial.print(pin);
	Serial.print(F(","));
	Serial.println(len);
#endif
	this->id = id;
	this->pin = pin;
	this->len = len;
	this->next = NULL;
	neopixel = new Adafruit_NeoPixel(len, pin, NEO_GRB+NEO_KHZ800);
	neopixel->begin();
}

/* destructor
 *
 * Destroy the neopixel instance
 */
strand_t::~strand_t()
{
#ifdef DEBUG
	Serial.print(F("Strand destroyed: "));
	Serial.println(this->id);
#endif
	delete(neopixel);
}

/*********************/
/* strandSet Methods */
/*********************/

/* Constructor
 *
 *
 */
strandSet::strandSet(void)
{
	head = NULL;
	len = 0;
}

/* lSize
 *
 * return the manually counted size of the linked list
 */
uint8_t strandSet::lSize()
{
	int counter = 0;
	strand_t * node = head;
	
	if (node != NULL)
		counter++;
	else
		return 0;
	
	while(node->next != 0){
		node = node->next;
		counter++;
	}
#ifdef DEBUG
	Serial.print(F("Size of strand is: "));
	Serial.println(counter);
	Serial.print(F("Len value is: "));
	Serial.println(len);
#endif
	return counter;
}


/* manageStrands
 *
 * @buffer, uint8_t *
 * @buflen, uint16_t buffer max length (at time of return, modified to be the length of the filled buffer)
 * @ret, uint8_t status value
 * returns a status containing the response to a strand request
 *
 */
//uint8_t manageStrands(uint8_t * buffer, uint16_t * buflen)

/* THIS METHOD CAUSED A LEONARDO TO GO APESHIT.  WE SHOULD BE PASSING AN ALLOCATED BUFFER BACK */
uint8_t strandSet::manageStrands(HardwareSerial * uart)
{
	/* This method should print out a count and every strand's id, pin and length */
#ifdef DEBUG
	Serial.println(F("manageStrands() called."));
#endif
	uint8_t ib = 0;
	uint8_t ia[2];

	strand_t * node = head;

	ib = lSize();


	if (ib == 0)
	{
#ifdef DEBUG
		Serial.println(F("manageStrands() lSize is zero."));
#endif
		return 1;
	}

#ifdef DEBUG
	Serial.println(F("manageStrands() lSize is NOT! zero."));
#endif

	delay(100);

	uart->write(ib);
#ifdef DEBUG
	Serial.print(F("Wrote IB: "));
	Serial.println(ib, HEX);
#endif

	// if (node != NULL)
	// {
	// 	uart->write(node->id);
	// 	uart->write(node->pin);

	// 	ia[0] = (uint8_t)(node->len >> 8) & 0xFF;
	// 	ia[1] = (uint8_t)(node->len) & 0xFF;

	// 	uart->write(ia,2);
	// }

	//while(node->next != NULL)
	while (node != NULL)
	{
		uart->write(node->id);
		uart->write(node->pin);

#ifdef DEBUG
		Serial.print(F("ms() id: "));
		Serial.println(node->id, HEX);

		Serial.print(F("ms() pin: "));
		Serial.println(node->pin, HEX);
#endif

		ia[0] = (uint8_t)(node->len >> 8) & 0xFF;
		ia[1] = (uint8_t)(node->len) & 0xFF;

#ifdef DEBUG
		for (int i=0; i<2; i++)
		{
			Serial.print(F("ms() len["));
			Serial.print(i);
			Serial.print(F("]: "));
			Serial.println(ia[i], HEX);
		}
#endif
		uart->write(ia,2);

		//memset(ia, 0, sizeof(uint8_t) * 2);
		if (node->next == NULL)
			break;
		node = node->next;
	}

#ifdef DEBUG
	Serial.println(F("manageStrands returning 0"));
#endif

	return 0;
}

/* getStrand
 *
 * @id, uint8_t, strand_t instance id to search for
 *
 * searches for a strand_t with id == id, then returns a pointer to it.
 */
strand_t * strandSet::getStrand(uint8_t id)
{
	strand_t * node = head;

#ifdef DEBUG
	Serial.print(F("getStrand id search: "));
	Serial.println(id);
#endif

	if(node == NULL) {
#ifdef DEBUG
		Serial.println(F("getStrand, head null."));
#endif
		return NULL;
	}
	
	if(node->id == id) {
#ifdef DEBUG
		Serial.print(F("getstrand, returning head for id - "));
		Serial.println(id);
#endif
		return node;
	}
	
	while (node->next != NULL)
	{
#ifdef DEBUG
		Serial.println(F("getstrand, while iter"));
		Serial.print(F("getstrand, cur id = "));
		Serial.println(node->id);
#endif
		if (node->id == id)
		{
#ifdef DEBUG
			Serial.println(F("getstrand match"));
#endif
			return node;
		}
		node = node->next;
	}
	
	if (node->id == id)
	{
#ifdef DEBUG
		Serial.println(F("getstrand match post-while"));
#endif
		return node;
	}
	
	return NULL;
}

strand_t * strandSet::getHead()
{
	if (head == NULL)
		return NULL;
		
	return head;
}

/* add
 *
 * @id, uint8_t, identifier to use for strand_t
 * @pin, uint8_t, pin used by strand_t's neopixel instance
 * @_len, uint16_t, length of strand_t's neopixel instance
 *
 * Adds a new value to the linked list.
 */
void strandSet::add(uint8_t id, uint8_t pin, uint16_t _len)
{
	strand_t * node = head;
	strand_t * lNode = NULL;

#ifdef DEBUG
		Serial.print(F("strandSet args("));
		Serial.print(id);
		Serial.print(F(","));
		Serial.print(pin);
		Serial.print(F(","));
		Serial.print(_len);
		Serial.println(F(")"));

#endif

	if (getStrand(id) != NULL)
	{
#ifdef DEBUG
		Serial.println("Strand already defined!");
#endif
		return;
	}

	lNode = new strand_t(id, pin, _len);
	
	if(node == NULL)
	{
#ifdef DEBUG
		Serial.println(F("add, node null."));
#endif
		head = lNode;
		++len; /* Why am I incrementing the local len? */
		return;
	}
	
	while(node->next != NULL)
	{
#ifdef DEBUG
		Serial.println(F("add, while node next..."));
#endif
		node = node->next;
	}
	
	node->next = lNode;
#ifdef DEBUG
	Serial.print(F("add, node next id = "));
	Serial.println(node->next->id);
	Serial.print(F("add, node prev id = "));
	Serial.println(node->id);
#endif
	++len; /* And /why/ here? */
}

/* del
 *
 * @id, uint8_t, strand_t identifier.
 *
 * deletes member with id == id
 */
void strandSet::del(uint8_t id)
{
#ifdef DEBUG
	Serial.print(F("del called, id:"));
	Serial.println(id);
#endif

	strand_t * node = head;
	strand_t * prev = NULL;

	while ( (node != NULL) && (node->id != id) )
	{
#ifdef DEBUG
		Serial.println("del while iter");
#endif
		prev = node;
		node = node->next;
	}

	if (node == NULL)
	{
#ifdef DEBUG
		Serial.println("del failed to find id.");
#endif
		return;
	}

	if (prev == NULL)
	{
#ifdef DEBUG
		Serial.println("del prev not null.");
#endif
		head = node->next;
	}
	else
	{
#ifdef DEBUG
		Serial.println("del prev null.");
#endif
		prev->next = node->next;
	}

	delete(node);
	node = NULL;
}


/* del
 *
 * deletes the last entry of the linked list
 */
void strandSet::del()
{
	strand_t * tmp_0 = NULL;
	strand_t * tmp_1 = NULL;
	strand_t * node = head;
	if (head->next == NULL)
	{
		delete(head);
		head = NULL;
		return;
	}
	
	tmp_0 = head->next;
	while(tmp_0->next != NULL)
	{
		tmp_1 = tmp_0;
		tmp_0 = tmp_0->next;
	}
	delete(tmp_0);
	len--;
	tmp_1->next = NULL;
}


/***********************/
/* UART_Neopixel begin */
/***********************/

/* Constructor
 * 
 * This is a blank for init during setup, so that begin(uart) can get called after
 */
UART_Neopixel::UART_Neopixel()
{

}

/* Constructor
 * 
 * @uart, HardwareSerial, This will call HardwareSerial.begin on baud rate @baud
 * @baud, baud rate to use
 */
UART_Neopixel::UART_Neopixel(HardwareSerial &uart, uint32_t baud)
{
	_uart = &uart;
	_uart->begin(baud);
}


UART_Neopixel::UART_Neopixel(HardwareSerial * uart)
{
	_uart = uart;
}

/* sUART
 *
 * @uart, HardwareSerial *
 *
 * Saves uart HardwareSerial instance pointer to class local
 */
void UART_Neopixel::sUART(HardwareSerial * uart)
{
	_uart = uart;
}


/* begin
 *
 * @uart, HardwareSerial
 *
 * Do not call this unless HardwareSerial.begin(<baudrate>) has been called before
 */
void UART_Neopixel::begin(HardwareSerial &uart)
{
#ifdef DEBUG
	Serial.println("It's happening!");
#endif
	_uart = &uart;
}

void UART_Neopixel::strandLedSet(strand_t * lStrand, uint16_t & pixel, uint32_t & color, bool show)
{
#ifdef DEBUG
	Serial.print(F("strandLedSet args (pix, color) ("));
	Serial.print(pixel,HEX);
	Serial.print(",");
	Serial.print(color,HEX);
	Serial.println(F(")"));
#endif

	lStrand->neopixel->setPixelColor(pixel, color);
	if (show)
		lStrand->neopixel->show();
}

/* handleMessage
 *
 * @llen, uint16_t, message length (Length of this->buf)
 * @return, uint8_t, 0 for a `successful` set, any other number for failure.
 */
uint8_t UART_Neopixel::handleMsg(uint8_t * buf, uint16_t llen)
{
	strand_t * lStrand;

	UART_Header header;
	UART_NP_XHeader xHeader;

	bool show = false;
	uint16_t pixel = 0;
	uint32_t color = 0, i = 0, fullHeaderLen = 0;

#ifdef DEBUG
	Serial.println(F("UNP called handleMsg"));
#endif

	/* populate the header data for easy access */
	for (i = 0; i < UART_MH_HEADER_SIZE; i++)
	{
		header.raw[i] = buf[i];
	}

	/* We've already got i right where we need it... */
	for (i; i < (UART_MH_HEADER_SIZE + UART_NP_XHEADER_SIZE); i++)
	{
		xHeader.raw[i] = buf[i];
	}

	fullHeaderLen = i;

	switch(header.data.scmd) /* We switch on the subcommand */
	{
		case UART_NP_SCMD_CTRLI: /* Immediate control, runs .show() on the neopixel instance after every setting change */
			show = true;
		case UART_NP_SCMD_CTRL:
			/* Check message body length */
			if ( (llen - fullHeaderLen) % UART_NP_CTRL_MSG_SIZE != 0)
				return 1;

			lStrand = strandSet_i.getStrand(xHeader.data.id);
			if (lStrand == NULL)
				return 2;

			/* i should not have changed yet */
			for (i; i < llen; i+=UART_NP_CTRL_MSG_SIZE)
			{
				color = lStrand->neopixel->Color(buf[i + 2], buf[i + 3], buf[i + 4]);
				pixel = ( (uint16_t)buf[i + 1] << 8 | (uint16_t)buf[i] );
				strandLedSet(lStrand, pixel, color, show);
			}

			lStrand->neopixel->show();
		 break;

		case UART_NP_SCMD_CLEAR:
			if ( (fullHeaderLen + UART_NP_CLEAR_MSG_SIZE) != llen )
				return 1;

			lStrand = strandSet_i.getStrand(xHeader.data.id);
			if (lStrand == NULL)
				return 2;

			lStrand->neopixel->clear();
			lStrand->neopixel->show();

		 break;

		case UART_NP_SCMD_MANAGE:
#ifdef DEBUG
			Serial.println(F("manage subcommand called."));
#endif
			if ( (llen - fullHeaderLen) != UART_NP_MANAGE_MSG_SIZE )
				return 1;

			for (i; i < llen; i++)
			{
				if (buf[i] != UART_NP_SCMD_MANAGE)
					return 2;
			}

			if (strandSet_i.manageStrands(_uart))
			{
#ifdef DEBUG
				Serial.println(F("Error from manageStrands, likely empty strand."));
#endif
				return 254;
			}
		 break;

		case UART_NP_SCMD_ADD:
			/* Check message body length */
			if ( (fullHeaderLen + UART_NP_ADD_MSG_SIZE) != llen )
				return 1;

			strandSet_i.add(xHeader.data.id,
				(uint8_t)buf[fullHeaderLen], //This was +1
				( (uint16_t)buf[fullHeaderLen + 2] << 8 | (uint16_t)buf[fullHeaderLen + 1] ) ); //And then this was +2 and +3

		 break;

		case UART_NP_SCMD_DEL:
			if ( (fullHeaderLen + UART_NP_DEL_MSG_SIZE) != llen)
			{
#ifdef DEBUG
				Serial.println(F("NPMsgH, llen error."));
#endif				
				return 1;
			}

			//if ( (buf[fullHeaderLen + 1] != xHeader.data.id) || (buf[fullHeaderLen + 2] != xHeader.data.id) )
			if ( (buf[fullHeaderLen] != xHeader.data.id) || (buf[fullHeaderLen + 1] != xHeader.data.id) )
			{
#ifdef DEBUG
				Serial.print(F("NPMsgH, header data error.  Data ID: "));
				Serial.println(xHeader.data.id, HEX);
#endif
				return 2;
			}

			strandSet_i.del(xHeader.data.id);
		 break;

		default:
#ifdef DEBUG
			Serial.println(F("default entry int uart handlemsg"));
#endif
			return 255;
	}

	return 0;
}