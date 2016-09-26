#include <Arduino.h>
//#include "Adafruit_NeoPixel.h"
#include "UART_Neopixel.h"
#include "UART_MessageHandler.h"

#ifndef UART_BASE_C
 #include "UART-BaseC.h"
#endif

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
	delete(neopixel);
}


/* get
 *
 * Dump all the data for every pixel on the strand to the supplied HardwareSerial pointer.
 */
void strand_t::get(BaseSerial_ * uart)
{
	uint16_t i = 0;
	uint32_u tmp;

	/* We want special messages for debugging here, so they'll be separated. */
	if (!uart)
		return;

	if (!neopixel)
		return;

	for (i; i < neopixel->numPixels(); i++)
	{
		tmp.data = neopixel->getPixelColor(i);
		uart->write(tmp.raw, 4);
	}

	uart->flush();
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

	return counter;
}

void strandSet::getAll(BaseSerial_ * uart)
{
	strand_t * node = head;

	uart->write(lSize());

	while(node != NULL)
	{
		node->get(uart);
		uart->print(UART_NP_GETALL_FILL);
		node = node->next;
	}
}

/* manageStrands
 *
 * @buffer, uint8_t *
 * @buflen, uint16_t buffer max length (at time of return, modified to be the length of the filled buffer)
 * @ret, uint8_t status value
 * returns a status containing the response to a strand request
 *
 */
uint8_t strandSet::manageStrands(BaseSerial_ * uart)
{
	uint8_t ib = 0;
	uint8_t ia[2];

	strand_t * node = head;

	ib = lSize();


	if (ib == 0)
	{
		return 1;
	}

	uart->write(ib);

	while (node != NULL)
	{
		uart->write(node->id);
		uart->write(node->pin);

		ia[0] = (uint8_t)(node->len >> 8) & 0xFF;
		ia[1] = (uint8_t)(node->len) & 0xFF;

		uart->write(ia,2);

		if (node->next == NULL)
			break;
		node = node->next;
	}

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

	if(node == NULL)
		return NULL;
	
	if(node->id == id)
		return node;
	
	while (node->next != NULL)
	{
		if (node->id == id)
			return node;

		node = node->next;
	}
	
	if (node->id == id)
		return node;
	
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

	if (getStrand(id) != NULL)
		return;

	lNode = new strand_t(id, pin, _len);
	
	if(node == NULL)
	{
		head = lNode;
		++len; /* Why am I incrementing the local len? */
		return;
	}
	
	while(node->next != NULL)
	{
		node = node->next;
	}
	
	node->next = lNode;
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
	strand_t * node = head;
	strand_t * prev = NULL;

	while ( (node != NULL) && (node->id != id) )
	{
		prev = node;
		node = node->next;
	}

	if (node == NULL)
		return;

	if (prev == NULL)
		head = node->next;
	else
		prev->next = node->next;

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
UART_Neopixel::UART_Neopixel(BaseSerial_ &uart, uint32_t baud)
{
	_uart = &uart;
	_uart->begin(baud);
}


UART_Neopixel::UART_Neopixel(BaseSerial_ * uart)
{
	_uart = uart;
}

/* sUART
 *
 * @uart, HardwareSerial *
 *
 * Saves uart HardwareSerial instance pointer to class local
 */
void UART_Neopixel::sUART(BaseSerial_ * uart)
{
	_uart = uart;
}


/* begin
 *
 * @uart, HardwareSerial
 *
 * Do not call this unless HardwareSerial.begin(<baudrate>) has been called before
 */
void UART_Neopixel::begin(BaseSerial_ &uart)
{
	_uart = &uart;
}

void UART_Neopixel::strandLedSet(strand_t * lStrand, uint16_t & pixel, uint32_t & color, bool show)
{
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

	/* populate the header data for easy access */
	for (i = 0; i < UART_MH_HEADER_SIZE; i++)
		header.raw[i] = buf[i];

	/* We've already got i right where we need it... */
	for (i; i < (UART_MH_HEADER_SIZE + UART_NP_XHEADER_SIZE); i++)
		xHeader.raw[i] = buf[i];

	fullHeaderLen = i;

	switch(header.data.scmd) /* We switch on the subcommand */
	{
		case UART_NP_SCMD_GET_ALL:
			if ( (fullHeaderLen + UART_NP_GET_MSG_SIZE) != llen )
				return 1;

			strandSet_i.getAll(_uart);
		 break;

		case UART_NP_SCMD_GET:
			if ( (fullHeaderLen + UART_NP_GET_A_MSG_SIZE) != llen )
				return 1;

			lStrand = strandSet_i.getStrand(xHeader.data.id);

			if (lStrand == NULL)
				return 2;

			lStrand->get(_uart);
		 break;

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
			if ( (llen - fullHeaderLen) != UART_NP_MANAGE_MSG_SIZE )
				return 1;

			for (i; i < llen; i++)
				if (buf[i] != UART_NP_SCMD_MANAGE)
					return 2;

			if (strandSet_i.manageStrands(_uart))
				return 254;

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
				return 1;

			if ( (buf[fullHeaderLen] != xHeader.data.id) || (buf[fullHeaderLen + 1] != xHeader.data.id) )
				return 2;

			strandSet_i.del(xHeader.data.id);
		 break;

		default:
			return 255;
	}

	return 0;
}