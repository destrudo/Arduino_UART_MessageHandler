# Arduino_UART_MessageHandler
Simple control for Digital pins and NeoPixels via UART commands

# Current State
This is well below anything that could be called stable or called a release; nor a candidate for a release.

If you use this in production without making it work yourself and then sending me patches, it might possibly put you on a self-destructive path.

Expect debugging messages to be turned on and off willy nilly between commits.

### Firmware
1. UART_MessageHandler
  - Possible Changes:
    * Possibility for actual C++ abstractness in adding new endpoint message handlers. *This would change a lot of stuff in terms of code, but it would still behave the same way.*
    * Adding in control methods for the UART_MH class for doing things such as manually setting limits.
    * A pin-in-use array that classes will respond to.
  - State:
    * Not going to change very much in the near future, pretty well tested where it stands currently.

2. UART_Neopixel
  - Possible Changes:
    * May split off each of the classes and structures into separate files.
    * A pin-in-use array that classes will respond to.
  - Going to Change:
    * Per-pin status requests on a wide scale which would return RGB data in order.
    * Failures when attempting to add strands that aren't plugged in.
  - State:
    * The protocol itself won't change, but there will be at least one more major addition.
    * It's tested and seems to work as expected.

3. UART_Digital
  - Possible Changes:
    * We might want to designate a pin to controlling an analog switch array or something (Which could be undone via management commands post-boot) so that as little effort as possible goes into using this in applications that can't start in the way that the bootloader will start. (A custom Arduino bootloader would fix this too.)
  - State:
    * Not rigorously tested.  Things seemed to work the last time I fiddled at them.

### Software
1. UARTMessageHandler
  - Possible Changes:
    * Too many to count, mostly cleanup and proper status handling.  Right now I check *everything* or cast *everything* when I don't really need to.
  - Going to Change:
    * Actual UART_Config class.  It too is blank.
  - State:
    * Relatively stable for UART_MH, UART_Digital and UART_Neopixel.  Everything else is empty.

2. MQTTHandler
  - Possible Changes:
    * Add *some* sort of abstraction so that I don't need to 'if' over a bunch of different types in the future
  - Going to Change:
    * Better thread cleanup
    * Posting of pixel states in management
    * Digital handling
  - State:
    * Extremely dirty but it does work.

# Protocol
The message protocol is a simple 12 byte command header for which the second to last bit is the sum of the preceeding 10 bytes.

####### If there's some nice lightweight open protocol with version information that works, which I overlooked... swing me a line.  I *really* would prefer to conform to an existing standard.

# Structure

- The base directory contains the firmware for easy extract into an Arduino brand libary path.
- There's one example (simple_memcheck) which uses a free memory checker, making it not compile on any ARM board without commenting out.  It did work fine on a Due once I got rid of that.
- The "controller" directory contains the UART_MessageHandler python lib and then two implementation applications.  One uses the MQTT stuff, the other just sends arbitrary messages in order to make it do small things.
