/* This is the most basic sample, ideally run on a leonardo or other some such
 * chip with at least 2 hardwareSerial interfaces.
 *
 * To get call data off of the device, uncomment #define DEBUG in uart_neopixel.h, it will use Serial.
 */
#define USE_UART_NEOPIXEL
#define USE_UART_DIGITAL

#include "Adafruit_NeoPixel.h"
#include "UART_Neopixel.h"
#include "UART_MessageHandler.h"

#include "MemoryFree.h"

UART_MessageHandler mh = UART_MessageHandler();
UART_Neopixel uart_np = UART_Neopixel();
uint16_t bufLen = 0;

void setup() {
  Serial.begin(115200);
  Serial1.begin(250000);
  
  mh.setUART(&Serial1);
  mh.configure(&uart_np); /* Configure the UART_Neopixel instance */
  delay(5000);
  Serial.println("Starting instance...");
}

void loop() {
  uint8_t status;
  if (Serial1.available())
  {
    bufLen = mh.run(status);
  }

  if (status)
  {
    Serial.println("mh.run() had bad status.");
  }
  
  /* We need to clear any message in the buffer (if allocated) */
  if (bufLen != 0)
  {
    mh.clear();
  }
  
  Serial.print("Free Memory: '");
  Serial.print(freeMemory());
  Serial.println("'");
  delay(100);
}


