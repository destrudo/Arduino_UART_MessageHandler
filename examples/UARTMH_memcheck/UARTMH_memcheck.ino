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
UART_Digital uart_digital = UART_Digital();
uint16_t bufLen = 0;
uint16_t printCount = 0;

void setup() {
  Serial.begin(115200);
  Serial1.begin(250000);
  
  mh.setUART(&Serial1);
  mh.configure(&uart_np); /* Configure the UART_Neopixel instance */
  mh.configure(&uart_digital);
  delay(2000);
  Serial.println("Starting instance...");
}

void loop() {
  uint8_t status;
  bufLen = 0;
  
  if (Serial1.available())
  {
    bufLen = mh.run(status);
  }

  if (status)
  {
    Serial.print("mh.run() had bad status: ");
    Serial.println(status);
  }
  
  /* We need to clear any message in the buffer (if allocated) */
  if (bufLen != 0)
  {
    Serial.print("Outside of loop, bufLen is: ");
    Serial.println(bufLen);
    bufLen = mh.clear();
  }
  
  printCount++;

  if (printCount >= 20000) {
    Serial.print("Free Memory: '");
    Serial.print(freeMemory());
    Serial.println("'");
    printCount = 0;
  }
}
