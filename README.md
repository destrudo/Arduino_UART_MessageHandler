﻿# Arduino_UART_MessageHandler
Simple control for Digital pins and NeoPixels via UART commands

# Current State
This is well below anything that could be called stable or called a release; nor a candidate for a release.

If you use this in production without making it work yourself and then sending me patches, it might possibly put you on a self-destructive path.

### Firmware
1. UART_MessageHandler
  Possible Changes:
  * Fixes for making digital management work.
  * Possibility for actual C++ abstractness in adding new endpoint message handlers. *This would change a lot of stuff in terms of code, but it would still behave the same way.*
  * Adding in control methods for the UART_MH class for doing things such as manually setting limits.
  * Adding in identification stuff so that Arduino 1 and Arduino 2 plugged into device 4 can be "tagged" by device 4 with a special key.  So if something gets mixed up during boot, I still know which is which.
  * A pin-in-use array that classes will respond to.
  Going to Change:
  * We need to dynamically adjust the current uart message limit to a per-board variable.  Currently it's a hard limit (And a short limit of *128 bytes* at that.)
  State:
  * Not going to change very much in the near future, pretty well tested where it stands currently.

2. UART_Neopixel
  Possible Changes:
  * May split off each of the classes and structures into separate files.
  * A pin-in-use array that classes will respond to.
  Going to Change:
  * Per-pin status requests on a wide scale which would return RGB data in order.
  * Failures when attempting to add strands that aren't plugged in.
  State:
  * The protocol itself won't change, but there will be at least one more major addition.
  * It's tested and seems to work as expected.

3. UART_Digital
  Possible Changes:
  * A pin-in-use array that classes will respond to.
  * We might want to designate a pin to controlling an analog switch array or something (Which could be undone via management commands post-boot) so that as little effort as possible goes into using this in applications that can't start in the way that the bootloader will start. (A custom Arduino bootloader would fix this too.)
  Going to change:
  * Possibly significant protocol adjustments.
  * Needs a management request/response method.
  * Needs a status structure to actually respond to those management requests.
  State:
  * Not rigorously tested.  Things seemed to work the last time I fiddled at them.
  * I haven't implemented half of the functionality I really wanted, just the bare minimum.

### Software
1. UARTMessageHandler
  Possible Changes:
  * Too many to count, mostly cleanup and proper status handling.  Right now I check *everything* or cast *everything* when I don't really need to.
  Going to Change
  * Actual UART_Digital class.  Currently it's a big blank.
  * Actual UART_Config class.  It too is blank.
  State
  * Relatively stable for UART_MH and UART_Neopixel.  Everything else is empty.

# Protocol
The message protocol is a simple 10 byte command header for which the last bit is the sum of the other 9 bytes.

The bytes, in order are:

- 0
[ 8b      ][         16b        ][   8b    ][   8b    ]
[   key   ][ cmd lo  ][ cmd hi  ][ subcmd  ][ version ]

- 5
[         16b        ][         16b        ][   8b    ]
[ out lo  ][ out hi  ][  in lo  ][  in hi  ][   sum   ]

Everything proceeding this header is not checksummed (Although I am considering checksumming the NeoPixel extended header data.)

####### If there's some nice lightweight open protocol with version information that works, which I overlooked... swing me a line.  I *really* would prefer to conform to an existing standard.

# Structure

- The base directory contains the firmware for easy extract into an Arduino brand libary path.
- There's one example (simple_memcheck) which uses a free memory checker, making it not compile on any ARM board without commenting out.  It did work fine on a Due once I got rid of that.
- The "controller" directory contains the UART_MessageHandler python lib and then two implementation applications.  One uses the MQTT stuff, the other just sends arbitrary messages in order to make it do small things.
