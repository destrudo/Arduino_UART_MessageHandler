#include <MemoryFree.h>
#include "Adafruit_NeoPixel.h"

#define MSG_BEGIN 0xaf /* stream sequence start message is to send command */
#define MSG_END 0x55 /* End sequence */

#define INIT_CTRL 0x88 /* Next sequence will be ctrl */
#define INIT_CMD 0x89 /* Next sequence will be cmd */

/* This is the initial control message so that we have it on hand whenever we
 *  need it (And so it can be easily filled in via buffer union)
 */
struct strandCtrlStartMessage {
	uint16_t numCtrl;
	uint8_t instance;
};

/* This is the structure that we'll read into in order to easily interpret the
 *  control values sent over uart.
 */
struct strandCtrlMessage {
	uint16_t pixel;
	uint8_t red;
	uint8_t green;
	uint8_t blue;
};

/* This is the structure that we'll read into in order to easily interpret the
 *  command type values sent over uart.
 */
struct strandCmdMessage {
	uint8_t cmd;
	uint8_t seq_begin;
	uint8_t seq_end;
};

/* We don't wanna keep it static for reasons of being really cool, so... LL. */
class strand_t {
 public:
  uint8_t id;
  uint8_t pin;
  uint16_t len;
  Adafruit_NeoPixel * neopixel;
  strand_t * next;

  strand_t(uint8_t id, uint8_t pin, uint16_t len)
  {
    Serial.print(F("Strand init, (id, pin, len) - "));
    Serial.print(id);
    Serial.print(F(","));
    Serial.print(pin);
    Serial.print(F(","));
    Serial.println(len);
    
    
   
    this->id = id;
    this->pin = pin;
    this->len = len;
    this->next = NULL;
    neopixel = new Adafruit_NeoPixel(len, pin, NEO_GRB+NEO_KHZ800);
    neopixel->begin();
/*
    neopixel->setPixelColor(len-1, neopixel->Color(100,100,100));
    neopixel->show();
*/
  }
  
  ~strand_t()
  {
    Serial.print(F("Strand destroyed: "));
    Serial.println(this->id);
    delete(neopixel);
  }
  
  strand_t * Next()
  {
    return next;
  }
};

class strandSet {
 private:
  strand_t * head;
//  strand_t * node;
  uint8_t len;
  
 public:
  strandSet(void);
  void add(uint8_t id, uint8_t pin, uint8_t len); /* add a new strand instance */
  void del(uint8_t id); /* Destroy strand based on ID */
  void del();
  void lSize();
  strand_t * getStrand(uint8_t id); /* Search for strand id */
  strand_t * getHead();
};

strandSet::strandSet(void)
{
  head = NULL;
  len = 0;
}

void strandSet::lSize()
{
  int counter = 0;
  strand_t * node = head;
  
  if (node != NULL)
    counter++;
  
  while(node->next != 0){
    node = node->next;
    counter++;
  }
  Serial.print(F("Size of strand is: "));
  Serial.println(counter);
  Serial.print(F("Len value is: "));
  Serial.println(len);
}

strand_t * strandSet::getStrand(uint8_t id)
{
  strand_t * node = head;
  
  if(node == NULL) {
    Serial.println(F("getStrand, head null."));

    return NULL;
  }
  
  if(node->id == id) {
    Serial.print(F("getstrand, returning head for id - "));
    Serial.println(id);

    return node;
  }
  
  while (node->next != NULL)
  {
    Serial.println(F("getstrand, while iter"));
    /* print node id */
    Serial.print(F("getstrand, cur id = "));
    Serial.println(node->id);
    if (node->id == id)
    {
      Serial.println(F("getstrand match"));
      return node;
    }
    node = node->next;
  }
  
  if (node->id == id)
  {
    Serial.println(F("getstrand match post-while"));
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

void strandSet::add(uint8_t id, uint8_t pin, uint8_t _len)
{
  strand_t * node = head;
  strand_t * lNode = new strand_t(id, pin, _len);
  
  if(node == NULL)
  {
    Serial.println(F("add, node null."));
    head = lNode;
    ++len;
    return;
  }
  
//  if(head->next == NULL) {
//    Serial.println(F("node next null, adding first"));
//    head->next = lNode;
//    ++len;
//    return;
//  }
  
  while(node->next != NULL)
  {
    Serial.println(F("add, while node next..."));
    node = node->next;
  }
  
  node->next = lNode;
  Serial.print(F("add, node next id = "));
  Serial.println(node->next->id);
  Serial.print(F("add, node prev id = "));
  Serial.println(node->id);
  ++len;
}

/* delete a particular ID */
void strandSet::del(uint8_t id)
{
  bool nodeFound = false;
  if (head == NULL)
  {
    return;
  }
  
  strand_t * prev = head;
  strand_t * tmp = NULL;
  strand_t * node = head;
  
  if (node->id == id) /* If the ID is the first one... */
  {
    head = node->next;
    delete(node);
    len = 0;
    return;
  }
  
  while(node->next != NULL)
  {
    Serial.println(F("delid, while node next not null"));
    tmp = node->next; /* The next node */
    
    if(node->id == id) {
      Serial.println(F("delid, while node found!"));
      delete(node);
      prev->next = tmp;
      len--;
      nodeFound = true; /* this will continue iterating */
    }
    
    prev = node; /* The previous node */
    node = node->next;
  }
  
  if (!nodeFound)
  {
    if(node->id == id) {
      delete(node);
      prev->next = NULL;
      len--;
      nodeFound = true;
    }
  }
  
  if(!nodeFound)
  {
    Serial.print(F("Failed to delete strand id: "));
    Serial.println(id);
  }
}

/* Delete the last list */
/* THIS NEEDS A RETURN VALUE FOR PROPER CONFIRMATION */
void strandSet::del()
{
  strand_t * tmp_0 = NULL;
  strand_t * tmp_1 = NULL;
  strand_t * node = head;
  if (head->next == NULL)
  {
    return;
  }
  
  tmp_0 = head->next;
  while(tmp_1->next != NULL)
  {
    tmp_1 = tmp_0;
    tmp_0 = tmp_0->next;
  }
  delete(tmp_0);
  len--;
  tmp_1->next = NULL;
}

strandSet strandSet_i = strandSet();


/* This should get integrated into a class which creates a strandSet instance. */
void handleMessage(uint8_t buf[], uint16_t llen)
{
  uint32_t counter = 5; /* We start at 5 to get the first pixel sequence */
  strand_t * lStrand;
  
  uint8_t cmd = 0;
  uint16_t cmds = 0;
  uint8_t id = 0;
  uint8_t pin = 0;
  
  /* These will be duplicated */
  uint16_t pixel = 0;
  uint8_t r = 0;
  uint8_t g = 0;
  uint8_t b = 0;
  /* to here... */
  
  strand_t * instance;
  
  if (llen == 0)
    return;
    
  Serial.print("Length of buffer: ");
  Serial.println(llen);
  
  /* Make sure the the command sequences are set as expected */
  if ( (buf[1] != 0xAA) || (buf[llen - 1] != 0x55) )
  {
    Serial.print(F("hM, command seq failed ("));
    Serial.print(buf[1],HEX);
    Serial.print(F(","));
//    Serial.print(buf[len-1], HEX);
    Serial.print(buf[llen - 1], HEX);
    Serial.println(F(")"));
    return;
  }
  
  if (cmd == 0x00) /* This is for setting pixels... */
  {
    /* We need to make sure that the length is valid */
    if ( (llen - 6) % 5 != 0 )
    {
      Serial.println(F("hM, bad message length."));
      return;
    }
  
    cmd = (uint8_t)buf[0];
    id = (uint8_t)buf[2];
    
    cmds = (uint16_t)buf[3] << 8 | (uint16_t)buf[4]; /* These might need to switch */
    Serial.print(F("hM, cmds = "));
    Serial.println(cmds);
  
  
    lStrand = strandSet_i.getStrand(id);
    if (lStrand == NULL)
    {
      Serial.print(F("hM, could not get strand: "));
      Serial.println(id);
    }
  
    /* We actually need to loop over number of commands following */
    for (counter = 5; counter < (llen - 2); (counter = counter + 5))
    {
      pixel = (uint16_t)buf[counter] << 8 | (uint32_t)buf[counter+1];
      r = buf[counter+2];
      g = buf[counter+3];
      b = buf[counter+4];
      Serial.print(F("hM, (pixel,r,g,b) = "));
      Serial.print(pixel);
      Serial.print(F(","));
      Serial.print(r);
      Serial.print(F(","));
      Serial.print(r);
      Serial.print(F(","));
      Serial.println(r);
      lStrand->neopixel->setPixelColor(pixel, lStrand->neopixel->Color(r,g,b));
      lStrand->neopixel->show();
    }
  }
  else if (cmd == 0x01) /* This is for adding new neopixel instances */
  {
    if (llen != 7)
      return;
    id = (uint8_t)buf[2];
    pin = (uint8_t)buf[3];
    cmds = (uint16_t)buf[4] << 8 | (uint16_t)buf[5]; /* Re-using the cmds variable for length*/
    /* add the id, cmds long */
    strandSet_i.add(id, pin, cmds);
  }
  else if (cmd == 0x02) /* Delete */
  {
    if (llen != 5)
      return;
    id = (uint8_t)buf[2];
    if (id != (uint8_t)buf[3])
    {
      Serial.println("hM, mismatched id's for delete command");
      return;
    }

    /* Delete the id */
    strandSet_i.del(id);
  }
  else if (cmd == 0x03) /* Clear */
  {
    Serial.println("hM, clearing.");
    if (llen != 4)
      return;
    id = (uint8_t)buf[2];
    Serial.print("id = ");
    Serial.println(id);
    instance = strandSet_i.getStrand(id);
    if (instance == NULL)
    {
      Serial.println("No such instance.");
      return;
    }

    instance->neopixel->clear();
  }
}

/* strandSet strandSet_i = strandSet(); */

void setup() {
  Serial.begin(115200);
  Serial.println(F("Began run..."));
  delay(5000); /* We want to make sure a lot of time goes by before initialization */
  strandSet_i.add(0,6,100);
  strandSet_i.lSize();
  strandSet_i.add(1,9,4);
  Serial.println(F("StrandSet initialized"));
  strandSet_i.lSize();
  strandSet_i.del(1);
  strandSet_i.lSize();
  strandSet_i.add(1,9,4);
  strandSet_i.lSize();
}

void loop() {
  uint8_t testB[128];
  
  Serial.print("freeMemory()=");
  Serial.println(freeMemory());
  strand_t * lStrand = strandSet_i.getStrand(0);
  if (lStrand != NULL) {
    lStrand->neopixel->clear();
    lStrand->neopixel->show();
    delay(100);
    lStrand->neopixel->setPixelColor(2, lStrand->neopixel->Color(20,20,20));
    lStrand->neopixel->show();
  } else {
    Serial.println(F("No lstrand()"));
  }
  
  strand_t * lStrand2 = strandSet_i.getStrand(1);
//  strand_t * lStrand2 = lStrand->Next();
  if (lStrand2 != NULL) {
    lStrand2->neopixel->clear();
    lStrand2->neopixel->show();
    delay(100);
    lStrand2->neopixel->setPixelColor(1, lStrand2->neopixel->Color(20,20,20));
    lStrand2->neopixel->show();
  } else {
    Serial.println(F("No lstrand2!"));
  }
  
  delay(100);
  testB[0] = 0x00;
  
  testB[1] = 0xAA;
  
  testB[2] = 0x01;
  
  testB[3] = 0x00;
  testB[4] = 0x00;
  
  testB[5] = 0x00;
  testB[6] = 0x00;
  
  testB[7] = 0x0f;
  
  testB[8] = 0x0f;
  
  testB[9] = 0x00;
  
  testB[10] = 0x55;
  
  testB[11] = 0x00;
  
  handleMessage(testB, 11);
  
  strandSet_i.del(1);
  strandSet_i.lSize();
  strandSet_i.add(1,9,4);
  strandSet_i.lSize();
  
  delay(100);
  testB[0] = 0x00;
  
  testB[1] = 0xAA;
  
  testB[2] = 0x00;
  
  testB[3] = 0x00;
  testB[4] = 0x02;
  
  testB[5] = 0x00; /* msg 1 */
  testB[6] = 0x02; 
  
  testB[7] = 0x0f;
  
  testB[8] = 0x0f;
  
  testB[9] = 0x00; /* msg 1 */
  
  testB[10] = 0x00; /* msg 2 */
  testB[11] = 0x03;
  
  testB[12] = 0x0f;
  
  testB[13] = 0x0f;
  
  testB[14] = 0x00; /* Msg 2 */
 
  testB[15] = 0x55;
  
  testB[16] = 0x00;
  
  handleMessage(testB, 16);  
  
  delay(200);
}
