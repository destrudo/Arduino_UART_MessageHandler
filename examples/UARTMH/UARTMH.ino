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
uint8_t printCount = 0;

void setup() {
  Serial.begin(115200);
  Serial1.begin(1000000);
  
  mh.setUART(&Serial1);
  mh.configure(&uart_np); /* Configure the UART_Neopixel instance */
  delay(2000);
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
    Serial.print("mh.run() had bad status: ");
    Serial.println(status);
  }
  
  /* We need to clear any message in the buffer (if allocated) */
  if (bufLen != 0)
  {
    bufLen = mh.clear();
  }
  
  printCount++;

  if (printCount >= 200) {
    Serial.print("Free Memory: '");
    Serial.print(freeMemory());
    Serial.println("'");
    printCount = 0;
  }
}
