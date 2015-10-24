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
uint8_t manageStrands(uint8_t * buffer, uint16_t * buflen)
{
	return 0;

/*
	uint8_t counter = 0;

	strand_t * node = head;

	if (node != NULL)
		counter++;

	while(node->next != NULL)
	{
		node->id;
		node->pin;
		node->
		node = node->next;
		counter++;
	}
*/
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
		++len;
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
	++len;
}

/* del
 *
 * @id, uint8_t, strand_t identifier.
 *
 * deletes member with id == id
 */
void strandSet::del(uint8_t id)
{
	bool nodeFound = false;
	if (head == NULL)
	{
		return;
	}
	
	strand_t * prev = head;
	//strand_t * tmp = NULL;
	strand_t * node = head;

	while(node != NULL)
	{
		if (node->id == id)
		{
			if (node->next != NULL)
			{
				if (prev != head)
					prev->next = node->next;
				else
					head = node->next;
			}
#ifdef DEBUG
			Serial.println("Deleting node!");
#endif
			delete(node);
			len--;
			nodeFound = true;
		}

		prev = node;
		node = node->next;
	}

/* The comments here are temporary, everything that's wrapped will likely get deleted. */
/*	
	if (node->id == id)
	{
		head = node->next;
		delete(node);
		len = 0;
		return;
	}
	
	while(node->next != NULL)
	{
#ifdef DEBUG
		Serial.println(F("delid, while node next not null"));
#endif
		tmp = node->next;
		
		if(node->id == id) {
#ifdef DEBUG
			Serial.println(F("delid, while node found!"));
#endif
			delete(node);
			prev->next = tmp;
			len--;
			nodeFound = true;
		}
		
		prev = node;
		node = node->next;
	}
*/

/*	
	if (!nodeFound)
	{
		if(node->id == id) {
			delete(node);
			prev->next = NULL;
			len--;
			nodeFound = true;
		}
	}
*/	
	if(!nodeFound)
	{
#ifdef DEBUG
		Serial.print(F("Failed to delete strand id: "));
		Serial.println(id);
#endif
	}
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

//void UART_Neopixel::strandLedSet(strand_t * lStrand, uint16_t * pixel, uint32_t * color, bool show)
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
// uint8_t UART_Neopixel::handleMsg(uint16_t llen)
// {
// 	uint32_t counter = 5; /* We start at 5 to get the first pixel sequence */
// 	strand_t * lStrand;
	
// 	uint8_t cmd = 0;
// 	uint16_t cmds = 0;
// 	uint8_t id = 0;
// 	uint8_t pin = 0;
	
// 	/* These will be duplicated */
// 	uint16_t pixel = 0;
// 	uint8_t r = 0;
// 	uint8_t g = 0;
// 	uint8_t b = 0;
// 	/* to here... */
	
// 	strand_t * instance;
	
// 	if (llen == 0)
// 		return 0; /* Ret 0 because length is zero, buf should get nuked. */

// 	cmd = buf[0]; /* Gotta set command... */

// #ifdef DEBUG		
// 	Serial.print("Length of buffer: ");
// 	Serial.println(llen);
// #endif

// 	/* Make sure the the command sequences are set as expected */
// 	if ( (buf[1] != 0xAA) || (buf[llen - 1] != 0x55) )
// 	{

// #ifdef DEBUG
// 		Serial.print(F("hM, command seq failed ("));
// 		Serial.print(buf[1],HEX);
// 		Serial.print(F(","));
// 		Serial.print(buf[llen - 1], HEX);
// 		Serial.println(F(")"));
// #endif

// 		return 1; /* If it's not our command sequence, return 1... */
// 	}
	
// 	if (cmd == 0x00) /* This is for setting pixels... */
// 	{
// 		/* We need to make sure that the length is valid */
// 		if ( (llen - 6) % 5 != 0 )
// 		{

// #ifdef DEBUG
// 			Serial.println(F("hM, bad message length."));
// #endif

// 			return 1; /* This is a little stranger, but if the message len is wrong, return 1 */
// 		}
	
// 		cmd = (uint8_t)buf[0];
// 		id = (uint8_t)buf[2];
		
// 		cmds = (uint16_t)buf[3] << 8 | (uint16_t)buf[4]; /* These might need to switch */

// #ifdef DEBUG
// 		Serial.print(F("hM, cmds = "));
// 		Serial.println(cmds);
// #endif

	
// 		lStrand = strandSet_i.getStrand(id);
// 		if (lStrand == NULL)
// 		{

// #ifdef DEBUG
// 			Serial.print(F("hM, could not get strand: "));
// 			Serial.println(id);
// #endif

// 		}
	
// 		 We actually need to loop over number of commands following 
// 		for (counter = 5; counter < (llen - 2); (counter = counter + 5))
// 		{
// 			pixel = (uint16_t)buf[counter] << 8 | (uint16_t)buf[counter+1];
// 			r = buf[counter+2];
// 			g = buf[counter+3];
// 			b = buf[counter+4];

// #ifdef DEBUG
// 			Serial.print(F("hM, (pixel,r,g,b) = "));
// 			Serial.print(pixel);
// 			Serial.print(F(","));
// 			Serial.print(r);
// 			Serial.print(F(","));
// 			Serial.print(r);
// 			Serial.print(F(","));
// 			Serial.println(r);
// #endif

// 			lStrand->neopixel->setPixelColor(pixel, lStrand->neopixel->Color(r,g,b));
// 			lStrand->neopixel->show();
// 		}
// 	}
// 	else if (cmd == 0x01) /* This is for adding new neopixel instances */
// 	{
// 		if (llen != 7)
// 			return 1;
// 		id = (uint8_t)buf[2];
// 		pin = (uint8_t)buf[3];
// 		cmds = (uint16_t)buf[4] << 8 | (uint16_t)buf[5]; /* Re-using the cmds variable for length*/
// 		/* add the id, cmds long */
// 		strandSet_i.add(id, pin, cmds);
// 	}
// 	else if (cmd == 0x02) /* Delete */
// 	{
// 		if (llen != 5)
// 			return 1;

// 		id = (uint8_t)buf[2];
// 		if (id != (uint8_t)buf[3])
// 		{

// #ifdef DEBUG
// 			Serial.println("hM, mismatched id's for delete command");
// #endif

// 			return 1;
// 		}

// 		/* Delete the id */
// 		strandSet_i.del(id);
// 	}
// 	else if (cmd == 0x03) /* Clear */
// 	{

// #ifdef DEBUG
// 		Serial.println("hM, clearing.");
// #endif

// 		if (llen != 4)
// 			return 1;
// 		id = (uint8_t)buf[2];

// #ifdef DEBUG
// 		Serial.print("id = ");
// 		Serial.println(id);
// #endif

// 		instance = strandSet_i.getStrand(id);
// 		if (instance == NULL)
// 		{

// #ifdef DEBUG
// 			Serial.println("No such instance.");
// #endif

// 			return 1;
// 		}

// 		instance->neopixel->clear();
// 		instance->neopixel->show();
// 	}
// 	else
// 	{
// 		return 1;
// 	}

// 	return 0;
// }











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
				pixel = ( (uint16_t)buf[i] << 8 | (uint16_t)buf[i + 1] );
				strandLedSet(lStrand, pixel, color, show);
			}
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

			if ( (buf[fullHeaderLen + 1] != xHeader.data.id) || (buf[fullHeaderLen + 2] != xHeader.data.id) )
				return 2;

			strandSet_i.del(xHeader.data.id);
		 break;

		default:
			return 255;
	}

	return 0;
}
	








/* readMsgD
 *
 * @return, uint16_t number of bytes read if handleMsg failed, if handleMsg worked, returns 0.
 *
 * reads the hardwareSerial _uart then calls handleMsg
 */
// uint16_t UART_Neopixel::readMsgD()
// {
// 	uint16_t msgLen = 0;
// 	uint8_t val;

// 	_buf = new uint8_t[1]; /* Do I actually need to perform this initialization? */

// 	while (_uart->available() > 0)
// 	{
// 		val = _uart->read();
// 		_buf = (uint8_t*) realloc(_buf, (msgLen + 1) * sizeof(uint8_t));
// 		_buf[msgLen] = (uint8_t)val;

// #ifdef DEBUG
// 		Serial.print("while avail: ");
// 		Serial.println(_buf[msgLen], HEX);
// #endif

// 		msgLen++;

// 		if (msgLen >= 128) /* The length we need to stop at is the max size of a uint16_t */
// 			break;
// 	}

// #ifdef DEBUG
// 	Serial.print("readMsg input: '0x");
// 	for (int i = 0; i < msgLen; i++)
// 	{
// 		Serial.print(_buf[i],HEX);
// 	}
// 	Serial.println("'");
// #endif

// 	if (handleMsg(msgLen) == 0)
// 	{

// #ifdef DEBUG
// 		Serial.println("HandleMsg returned 0, nuking the buffer.");
// #endif

// 		clear();
// 		return 0;
// 	}

// 	return msgLen;
// }

/* clear
 *
 * calls delete on buf (If it's set)
 */
// void UART_Neopixel::clear()
// {
// 	if (buf != NULL)
// 	{
// 		delete _buf;
// 		buf = NULL;
// 	}
// }

/* getBuf
 *
 * @return, uint8_t *, pointer to buf.
 */
// uint8_t * UART_Neopixel::getBuf()
// {
// 	return _buf;
// }